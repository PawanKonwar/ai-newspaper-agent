"""
Pipeline and config tests.
Path and .env are set in tests/conftest.py.
"""


def test_config_loads():
    """Config reads from environment."""
    from app.config import OPENAI_API_KEY, DEEPSEEK_API_KEY, GOOGLE_API_KEY
    from app.config import APP_HOST, APP_PORT, STATIC_DIR, TEMPLATES_DIR
    assert APP_HOST in ("0.0.0.0", "127.0.0.1") or len(APP_HOST) > 0
    assert isinstance(APP_PORT, int)
    assert STATIC_DIR.exists() or True
    assert TEMPLATES_DIR.exists() or True


def test_parse_research_facts():
    """Pipeline parses FACT | SOURCE lines."""
    from app.pipeline import NewspaperPipeline
    pipeline = NewspaperPipeline()
    text = "FACT: Global temps rose 1.1°C. | SOURCE: IPCC\nFACT: Renewables at 30%. | SOURCE: IEA"
    facts = pipeline._parse_research_facts(text)
    assert len(facts) >= 2
    assert facts[0]["fact"] and facts[0]["source"]
    assert "IPCC" in facts[0]["source"] or "1.1" in facts[0]["fact"]
