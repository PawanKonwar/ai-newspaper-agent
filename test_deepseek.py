#!/usr/bin/env python3
"""
Test script to debug DeepSeek API integration
"""

import asyncio
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("env.env")

async def test_deepseek():
    """Test DeepSeek API directly."""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    print(f"API Key: {api_key[:10]}..." if api_key else "No API key found")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "Hello, this is a test message"}],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    try:
        async with httpx.AsyncClient() as client:
            print("Making request to DeepSeek API...")
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30.0
            )
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Success!")
                print(f"Response: {result['choices'][0]['message']['content']}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response text: {response.text}")
                
    except Exception as e:
        print(f"❌ Exception: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_deepseek())
