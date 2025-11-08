import os
import asyncio
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

async def test_gemini_connection():
    """Test if Gemini API key and connection are working"""
    api_key = os.getenv("GEMINI_API_KEY")
    
    print("Gemini API Connection Test")
    print("-" * 50)
    
    # Phase 1: Check if API key exists
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY not found in environment variables")
        print("   Make sure you have a .env file with GEMINI_API_KEY=your_key")
        return False
        
    # Phase 2: Check API key format
    if not api_key.startswith("AIza"):
        print("❌ ERROR: Invalid API key format")
        print("   Gemini API keys should start with 'AIza'")
        return False
    
    print("✓ API key format looks valid")
    print(f"   Key starts with: {api_key[:6]}...")
    
    # Phase 3: Test actual API connection
    try:
        print("\nTesting API connection...")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Try to generate a simple response
        response = model.generate_content("Respond with 'OK' if you can read this.")
        
        if response and response.text:
            print("✅ SUCCESS: API connection working!")
            print(f"   Test response: {response.text[:50]}...")
            return True
        else:
            print("❌ ERROR: No response received from API")
            return False
            
    except Exception as e:
        print("❌ ERROR: Failed to connect to Gemini API")
        print(f"   Error: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_gemini_connection())