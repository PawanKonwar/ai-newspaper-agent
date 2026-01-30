"""
Three-stage pipeline: Research (DeepSeek) → Draft (OpenAI) → Edit (Google Gemini).
All API keys are read from app.config (loaded from .env).
"""

import logging
import re
from typing import Any, Dict, List

import httpx
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from .config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    GEMINI_EDIT_MODEL,
    GEMINI_FALLBACK_MODEL,
    GOOGLE_API_KEY,
    OPENAI_API_KEY,
)

logger = logging.getLogger(__name__)


# Token limits: stricter for short articles (<200 words)
def word_count_to_max_tokens(word_count: int) -> int:
    """Convert target word count to max_tokens for API calls."""
    if word_count < 200:
        return max(50, int(word_count * 1.1))
    return max(100, int(word_count * 1.33))


def _truncate_to_word_count(text: str, target_words: int) -> str:
    """Truncate at sentence boundary if >20% over target."""
    if not text or target_words <= 0:
        return text
    words = text.split()
    if len(words) <= int(target_words * 1.2):
        return text
    sentences = re.split(r"(?<=[.!?])\s+", text)
    result: list[str] = []
    count = 0
    for s in sentences:
        s_words = len(s.split())
        if count + s_words <= target_words:
            result.append(s)
            count += s_words
        else:
            break
    truncated = " ".join(result).strip()
    if not truncated:
        truncated = " ".join(words[:target_words])
    return truncated


def _count_words(text: str) -> int:
    """Return word count (split on whitespace)."""
    return len(text.split()) if text else 0


class DeepSeekLLM:
    """DeepSeek API wrapper for the research stage."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def agenerate(self, prompt: str, **kwargs) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2000,
        }
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    DEEPSEEK_BASE_URL, headers=headers, json=data
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            detail = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.exception("DeepSeek API HTTP error: %s", detail)
            raise RuntimeError(f"DeepSeek API error: {detail}") from e
        except httpx.TimeoutException:
            logger.exception("DeepSeek API request timed out")
            raise RuntimeError("DeepSeek API error: Request timeout") from None
        except Exception as e:
            logger.exception("DeepSeek API error: %s", e)
            raise RuntimeError(f"DeepSeek API error: {str(e)}") from e


class NewspaperPipeline:
    """Orchestrates Research → Draft → Edit stages."""

    def __init__(self) -> None:
        self.deepseek_api_key = DEEPSEEK_API_KEY
        self.openai_api_key = OPENAI_API_KEY
        self.google_api_key = GOOGLE_API_KEY

        if not self.deepseek_api_key:
            logger.warning("DEEPSEEK_API_KEY not set - Research stage unavailable")
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY not set - Draft stage unavailable")
        if not self.google_api_key:
            logger.warning("GOOGLE_API_KEY not set - Edit stage unavailable")

        self.deepseek_llm = (
            DeepSeekLLM(self.deepseek_api_key) if self.deepseek_api_key else None
        )
        self.openai_llm = (
            ChatOpenAI(
                api_key=self.openai_api_key,
                model="gpt-4-turbo-preview",
                temperature=0.7,
            )
            if self.openai_api_key
            else None
        )
        self.gemini_edit_model = GEMINI_EDIT_MODEL
        self.gemini_edit_fallback_model = GEMINI_FALLBACK_MODEL
        self.gemini_llm = (
            ChatGoogleGenerativeAI(
                model=self.gemini_edit_model,
                google_api_key=self.google_api_key,
                temperature=0.5,
                convert_system_message_to_human=True,
            )
            if self.google_api_key
            else None
        )

    async def research_stage(
        self, topic: str, max_length: int = 1000
    ) -> Dict[str, Any]:
        if not self.deepseek_llm:
            logger.error("Research: DEEPSEEK_API_KEY not configured")
            return {
                "status": "error",
                "message": "DeepSeek API key not configured",
                "research_data": "Research stage unavailable",
                "research_facts": [],
            }

        if max_length < 150:
            fact_instruction = (
                "Provide at most 3 facts. Very brief. One line per fact."
            )
        elif max_length <= 500:
            fact_instruction = "Provide 5-7 facts. Concise."
        else:
            fact_instruction = "Provide 10-15 facts (full research)."

        research_prompt = f'''Research the topic: "{topic}"

{fact_instruction}

For each finding, use this exact format on its own line:
FACT: <the finding or statistic> | SOURCE: <source name, study, or citation>

Example:
FACT: Global temperatures have risen 1.1°C since pre-industrial. | SOURCE: IPCC
FACT: Renewable energy 30% of global electricity in 2024. | SOURCE: IEA

Do not exceed facts requested. Keep concise for {max_length}-word article.'''

        try:
            research_data = await self.deepseek_llm.agenerate(research_prompt)
            research_facts = self._parse_research_facts(research_data)
            return {
                "status": "success",
                "message": "Research completed successfully",
                "research_data": research_data,
                "research_facts": research_facts,
                "llm_used": "DeepSeek Chat",
            }
        except Exception as e:
            error_msg = str(e) or "Unknown error occurred"
            logger.exception("Research stage failed: %s", error_msg)
            return {
                "status": "error",
                "message": f"Research failed: {error_msg}",
                "research_data": f"Research stage encountered an error: {error_msg}",
                "research_facts": [],
            }

    def _parse_research_facts(self, research_data: str) -> List[Dict[str, str]]:
        facts = []
        for line in (research_data or "").strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "FACT:" in line and "|" in line and "SOURCE:" in line:
                try:
                    fact_part, source_part = line.split("|", 1)
                    fact = fact_part.replace("FACT:", "").strip()
                    source = source_part.replace("SOURCE:", "").strip()
                    if fact and source:
                        facts.append({"fact": fact, "source": source})
                except ValueError:
                    facts.append({"fact": line, "source": "DeepSeek Research"})
            elif line:
                facts.append({"fact": line, "source": "DeepSeek Research"})
        return facts

    async def draft_stage(
        self, topic: str, research_data: str, max_length: int = 1200
    ) -> Dict[str, Any]:
        if not self.openai_llm:
            logger.error("Draft: OPENAI_API_KEY not configured")
            return {
                "status": "error",
                "message": "OpenAI API key not configured",
                "draft_content": "Draft stage unavailable",
            }

        is_blurb = max_length < 150
        is_short = max_length < 200 and not is_blurb
        max_tokens = word_count_to_max_tokens(max_length)
        if is_blurb:
            draft_prompt = (
                f'''Based on this research, write a VERY BRIEF news blurb of '''
                f'''exactly {max_length} words about "{topic}".

Research Data:
{research_data}

Requirements:
- Write a VERY BRIEF news blurb of exactly {max_length} words.
- Just 2-3 key points. No introduction or conclusion needed.
- One short paragraph is fine. Be direct.
- Use FACT: ... | SOURCE: ... only as background; write the blurb in normal prose.
'''
            )
        else:
            concise_instruction = (
                "\nCRITICAL: VERY CONCISE. NO FLUFF. Every sentence must earn "
                "its place.\n"
                if is_short
                else ""
            )
            draft_prompt = f'''
Based on the research below, write a compelling newspaper article about "{topic}".
{concise_instruction}
Research Data:
{research_data}

Requirements:
- Write in a professional journalistic style
- Include a compelling headline
- Structure with clear paragraphs
- Include relevant facts and context
- Maintain objectivity and accuracy
- Target length: approximately {max_length} words (strict limit)
- Use proper news article formatting

Provide the complete article draft. Do not exceed {max_length} words.
'''

        try:
            draft_llm = ChatOpenAI(
                api_key=self.openai_api_key,
                model="gpt-4-turbo-preview",
                temperature=0.7,
                max_tokens=max_tokens,
            )
            response = await draft_llm.ainvoke(draft_prompt)
            draft_content = (
                response.content
                if hasattr(response, "content")
                else str(response)
            )
            draft_content = _truncate_to_word_count(draft_content, max_length)
            final_words = _count_words(draft_content)
            return {
                "status": "success",
                "message": "Draft generated successfully",
                "draft_content": draft_content,
                "llm_used": "OpenAI GPT-4 Turbo",
                "word_count": final_words,
                "target_word_count": max_length,
            }
        except Exception as e:
            logger.exception("Draft stage failed: %s", e)
            return {
                "status": "error",
                "message": f"Draft generation failed: {str(e)}",
                "draft_content": "Draft stage encountered an error",
            }

    async def edit_stage(
        self, topic: str, draft_content: str, max_length: int = 1200
    ) -> Dict[str, Any]:
        if not self.gemini_llm:
            logger.error("Edit: GOOGLE_API_KEY not configured")
            return {
                "status": "error",
                "message": "Google Gemini API key not configured",
                "final_content": "Edit stage unavailable",
            }

        is_short = max_length < 200
        concise_instruction = (
            " CRITICAL: VERY CONCISE. NO FLUFF. Do not add length."
            if is_short
            else ""
        )
        max_output_tokens = word_count_to_max_tokens(max_length)
        edit_prompt = f'''
As an experienced editor, review and polish the following article about "{topic}":
{concise_instruction}

{draft_content}

Please:
1. Improve clarity and flow
2. Enhance readability and engagement
3. Ensure proper grammar and style
4. Optimize headline for impact
5. Add compelling subheadings if needed (only if length allows)
6. Maintain journalistic integrity
7. Ensure the article is publication-ready

Provide the final polished version. Keep length ~{max_length} words max.
'''

        messages = [
            SystemMessage(
                content=(
                    "You are an experienced newspaper editor with expertise "
                    "in polishing journalistic content."
                )
            ),
            HumanMessage(content=edit_prompt),
        ]

        try:
            edit_llm = ChatGoogleGenerativeAI(
                model=self.gemini_edit_model,
                google_api_key=self.google_api_key,
                temperature=0.5,
                max_output_tokens=max_output_tokens,
                convert_system_message_to_human=True,
            )
            response = await edit_llm.ainvoke(messages)
            final_content = (
                response.content
                if hasattr(response, "content")
                else str(response)
            )
            final_content = _truncate_to_word_count(final_content, max_length)
            final_words = _count_words(final_content)
            return {
                "status": "success",
                "message": "Article polished successfully",
                "final_content": final_content,
                "llm_used": f"Google Gemini ({self.gemini_edit_model})",
                "word_count": final_words,
                "target_word_count": max_length,
            }
        except Exception as e:
            if "not found" in str(e).lower() or "404" in str(e):
                logger.warning(
                    "Edit: %s unavailable, trying fallback %s",
                    self.gemini_edit_model,
                    self.gemini_edit_fallback_model,
                )
                try:
                    fallback_llm = ChatGoogleGenerativeAI(
                        model=self.gemini_edit_fallback_model,
                        google_api_key=self.google_api_key,
                        temperature=0.5,
                        max_output_tokens=max_output_tokens,
                        convert_system_message_to_human=True,
                    )
                    response = await fallback_llm.ainvoke(messages)
                    final_content = (
                        response.content
                        if hasattr(response, "content")
                        else str(response)
                    )
                    final_content = _truncate_to_word_count(
                        final_content, max_length
                    )
                    final_words = _count_words(final_content)
                    fallback_llm_name = (
                        f"Google Gemini ({self.gemini_edit_fallback_model})"
                    )
                    return {
                        "status": "success",
                        "message": "Article polished successfully",
                        "final_content": final_content,
                        "llm_used": fallback_llm_name,
                        "word_count": final_words,
                        "target_word_count": max_length,
                    }
                except Exception as fallback_e:
                    logger.exception("Edit stage failed (fallback): %s", fallback_e)
                    return {
                        "status": "error",
                        "message": f"Editing failed: {str(fallback_e)}",
                        "final_content": "Edit stage encountered an error",
                    }
            logger.exception("Edit stage failed: %s", e)
            return {
                "status": "error",
                "message": f"Editing failed: {str(e)}",
                "final_content": "Edit stage encountered an error",
            }

    async def run_pipeline(
        self, topic: str, max_length: int = 1000
    ) -> Dict[str, Any]:
        research_result = await self.research_stage(topic, max_length)

        if research_result["status"] == "success":
            draft_result = await self.draft_stage(
                topic, research_result["research_data"], max_length
            )
        else:
            draft_result = {
                "status": "skipped",
                "message": "Draft stage skipped due to research failure",
                "draft_content": "Cannot generate draft without research data",
            }

        if draft_result["status"] == "success":
            edit_result = await self.edit_stage(
                topic, draft_result["draft_content"], max_length
            )
        else:
            edit_result = {
                "status": "skipped",
                "message": "Edit stage skipped due to draft failure",
                "final_content": "Cannot edit without draft content",
            }

        return {
            "research_stage": research_result,
            "draft_stage": draft_result,
            "final_stage": edit_result,
        }
