import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
from src.analyzer import BackstoryAnalyzer

# Mock payload to test flow if no API key is present
# In a real scenario, we expect GEMINI_API_KEY to be in the environment
async def main():
    print("Testing BackstoryAnalyzer...")
    
    # Check for API Key (just a warning, not stopping)
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("WARNING: No API Key found in environment. Calls might fail or hit fallback.")
    
    # Updated to use Grok (xAI)
    analyzer = BackstoryAnalyzer(llm_config={"model": "xai/grok-beta"})
    
    sample_text = "The library, which was built in 1890, burned down in 1995. Mayor Thomas rebuilt it two years later."
    
    print(f"\nInput: {sample_text}")
    print("Extracting claims...")
    
    try:
        claims = await analyzer.extract_atomic_claims(sample_text)
        print("\n--- Atomic Claims ---")
        for i, claim in enumerate(claims, 1):
            print(f"{i}. {claim}")
            
        if not claims:
            print("No claims extracted (possible error).")
            
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    asyncio.run(main())
