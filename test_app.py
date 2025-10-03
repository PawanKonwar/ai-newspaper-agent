"""
Test script for AI Newspaper Agent
Simple validation of the application components
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from newspaper_pipeline import NewspaperPipeline

async def test_pipeline():
    """Test the newspaper pipeline with a sample topic."""
    
    # Load environment variables
    load_dotenv("env.env")
    
    # Check if API keys are configured
    required_keys = ['OPENAI_API_KEY', 'DEEPSEEK_API_KEY', 'GOOGLE_API_KEY']
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        print(f"⚠️  Missing API keys: {', '.join(missing_keys)}")
        print("Please configure your API keys in the .env file")
        return False
    
    print("✅ All API keys are configured")
    
    # Initialize pipeline
    try:
        pipeline = NewspaperPipeline()
        print("✅ Pipeline initialized successfully")
    except Exception as e:
        print(f"❌ Pipeline initialization failed: {e}")
        return False
    
    # Test with a sample topic
    test_topic = "Artificial Intelligence in Healthcare"
    print(f"\n🧪 Testing with topic: '{test_topic}'")
    
    try:
        result = await pipeline.run_pipeline(test_topic, max_length=800)
        
        # Check results
        print("\n📊 Pipeline Results:")
        print(f"Research Stage: {result['research_stage']['status']}")
        print(f"Draft Stage: {result['draft_stage']['status']}")
        print(f"Final Stage: {result['final_stage']['status']}")
        
        # Display sample content
        if result['research_stage']['status'] == 'success':
            research_preview = result['research_stage']['research_data'][:200] + "..."
            print(f"\n🔍 Research Preview: {research_preview}")
        
        if result['draft_stage']['status'] == 'success':
            draft_preview = result['draft_stage']['draft_content'][:200] + "..."
            print(f"\n✍️  Draft Preview: {draft_preview}")
        
        if result['final_stage']['status'] == 'success':
            final_preview = result['final_stage']['final_content'][:200] + "..."
            print(f"\n✨ Final Preview: {final_preview}")
        
        print("\n✅ Pipeline test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn imported successfully")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    try:
        import langchain
        print("✅ LangChain imported successfully")
    except ImportError as e:
        print(f"❌ LangChain import failed: {e}")
        return False
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("✅ Google Gemini integration imported successfully")
    except ImportError as e:
        print(f"❌ Google Gemini import failed: {e}")
        return False
    
    return True

def main():
    """Main test function."""
    print("🚀 AI Newspaper Agent - Test Suite")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please install missing dependencies:")
        print("pip install -r requirements.txt")
        return
    
    print("\n" + "=" * 50)
    
    # Test pipeline
    try:
        result = asyncio.run(test_pipeline())
        if result:
            print("\n🎉 All tests passed! The application is ready to run.")
            print("\nTo start the application, run:")
            print("python main.py")
        else:
            print("\n⚠️  Some tests failed. Please check the configuration.")
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")

if __name__ == "__main__":
    main()
