"""
Newspaper Pipeline - Core LLM Orchestration Logic
Implements the three-stage pipeline: Research → Draft → Edit
"""

import os
import asyncio
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv("env.env")
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.callbacks.manager import CallbackManagerForLLMRun
import httpx
import json

class DeepSeekLLM:
    """Custom DeepSeek LLM wrapper for research stage."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
    
    async def agenerate(self, prompt: str, **kwargs) -> str:
        """Generate response from DeepSeek API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(self.base_url, headers=headers, json=data)
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            error_detail = f"HTTP {e.response.status_code}: {e.response.text}"
            raise Exception(f"DeepSeek API error: {error_detail}")
        except httpx.TimeoutException:
            raise Exception("DeepSeek API error: Request timeout")
        except Exception as e:
            raise Exception(f"DeepSeek API error: {str(e)}")

class NewspaperPipeline:
    """Main pipeline orchestrating the three-stage article generation process."""
    
    def __init__(self):
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        
        # Initialize LLMs
        self.deepseek_llm = DeepSeekLLM(self.deepseek_api_key) if self.deepseek_api_key else None
        self.openai_llm = ChatOpenAI(
            api_key=self.openai_api_key,
            model="gpt-4-turbo-preview",
            temperature=0.7,
            max_tokens=2000
        ) if self.openai_api_key else None
        self.gemini_llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=self.google_api_key,
            temperature=0.5,
            max_output_tokens=2000,
            convert_system_message_to_human=True
        ) if self.google_api_key else None
    
    async def research_stage(self, topic: str) -> Dict[str, Any]:
        """
        Stage 1: Research using DeepSeek
        Gathers comprehensive information about the topic.
        """
        if not self.deepseek_llm:
            return {
                "status": "error",
                "message": "DeepSeek API key not configured",
                "research_data": "Research stage unavailable"
            }
        
        research_prompt = f"""Research the topic: "{topic}"

Provide key information including:
- Main facts and recent developments
- Important statistics or data points
- Expert insights or quotes
- Current trends and implications

Keep the response concise but informative for writing a news article."""
        
        try:
            research_data = await self.deepseek_llm.agenerate(research_prompt)
            return {
                "status": "success",
                "message": "Research completed successfully",
                "research_data": research_data,
                "llm_used": "DeepSeek Chat"
            }
        except Exception as e:
            error_msg = str(e) if str(e) else "Unknown error occurred"
            return {
                "status": "error",
                "message": f"Research failed: {error_msg}",
                "research_data": f"Research stage encountered an error: {error_msg}"
            }
    
    async def draft_stage(self, topic: str, research_data: str) -> Dict[str, Any]:
        """
        Stage 2: Draft generation using OpenAI
        Creates an initial article draft based on research.
        """
        if not self.openai_llm:
            return {
                "status": "error",
                "message": "OpenAI API key not configured",
                "draft_content": "Draft stage unavailable"
            }
        
        draft_prompt = f"""
        Based on the following research data, write a compelling newspaper article about "{topic}".
        
        Research Data:
        {research_data}
        
        Requirements:
        - Write in a professional journalistic style
        - Include a compelling headline
        - Structure with clear paragraphs
        - Include relevant facts and context
        - Maintain objectivity and accuracy
        - Target length: 800-1200 words
        - Use proper news article formatting
        
        Please provide the complete article draft.
        """
        
        try:
            # Use the invoke method instead of agenerate for better compatibility
            response = await self.openai_llm.ainvoke(draft_prompt)
            draft_content = response.content if hasattr(response, 'content') else str(response)
            return {
                "status": "success",
                "message": "Draft generated successfully",
                "draft_content": draft_content,
                "llm_used": "OpenAI GPT-4 Turbo"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Draft generation failed: {str(e)}",
                "draft_content": "Draft stage encountered an error"
            }
    
    async def edit_stage(self, topic: str, draft_content: str) -> Dict[str, Any]:
        """
        Stage 3: Final editing using Google Gemini
        Polishes and refines the article for publication.
        """
        if not self.gemini_llm:
            return {
                "status": "error",
                "message": "Google Gemini API key not configured",
                "final_content": "Edit stage unavailable"
            }
        
        edit_prompt = f"""
        As an experienced newspaper editor, please review and polish the following article about "{topic}":
        
        {draft_content}
        
        Please:
        1. Improve clarity and flow
        2. Enhance readability and engagement
        3. Ensure proper grammar and style
        4. Optimize headline for impact
        5. Add compelling subheadings if needed
        6. Maintain journalistic integrity
        7. Ensure the article is publication-ready
        
        Provide the final polished version of the article.
        """
        
        try:
            messages = [
                SystemMessage(content="You are an experienced newspaper editor with expertise in polishing journalistic content."),
                HumanMessage(content=edit_prompt)
            ]
            response = await self.gemini_llm.ainvoke(messages)
            final_content = response.content if hasattr(response, 'content') else str(response)
            return {
                "status": "success",
                "message": "Article polished successfully",
                "final_content": final_content,
                "llm_used": "Google Gemini Pro"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Editing failed: {str(e)}",
                "final_content": "Edit stage encountered an error"
            }
    
    async def run_pipeline(self, topic: str, max_length: int = 1000) -> Dict[str, Any]:
        """
        Execute the complete three-stage pipeline.
        
        Args:
            topic: The subject for the article
            max_length: Maximum length for the final article
            
        Returns:
            Dictionary containing results from all three stages
        """
        # Stage 1: Research
        research_result = await self.research_stage(topic)
        
        # Stage 2: Draft (only if research was successful)
        if research_result["status"] == "success":
            draft_result = await self.draft_stage(topic, research_result["research_data"])
        else:
            draft_result = {
                "status": "skipped",
                "message": "Draft stage skipped due to research failure",
                "draft_content": "Cannot generate draft without research data"
            }
        
        # Stage 3: Edit (only if draft was successful)
        if draft_result["status"] == "success":
            edit_result = await self.edit_stage(topic, draft_result["draft_content"])
        else:
            edit_result = {
                "status": "skipped",
                "message": "Edit stage skipped due to draft failure",
                "final_content": "Cannot edit without draft content"
            }
        
        return {
            "research_stage": research_result,
            "draft_stage": draft_result,
            "final_stage": edit_result
        }
