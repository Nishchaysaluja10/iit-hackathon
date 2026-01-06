import asyncio
import json
from unittest.mock import AsyncMock, patch
from src.analyzer import BackstoryAnalyzer, ExtractionResponse, AtomicFact

# Mock JSON response from LLM
MOCK_LLM_RESPONSE = json.dumps({
    "facts": [
        {"fact": "The library was built in 1890."},
        {"fact": "The library burned down in 1995."},
        {"fact": "Mayor Thomas rebuilt the library two years later."}
    ]
})

async def main():
    print("Testing BackstoryAnalyzer with MOCK LLM to verify logic...")
    
    analyzer = BackstoryAnalyzer()
    
    # We mock the internal _call_llm or litellm.acompletion
    # Since we use litellm.acompletion in src/analyzer.py, we patch it here.
    with patch("src.analyzer.acompletion") as mock_completion:
        # Setup mock return value structure (resembling OpenAI/LiteLLM response)
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = MOCK_LLM_RESPONSE
        mock_completion.return_value = mock_response
        
        sample_text = "The library, which was built in 1890, burned down in 1995. Mayor Thomas rebuilt it two years later."
        print(f"\nInput: {sample_text}")
        
        # Run extraction
        claims = await analyzer.extract_atomic_claims(sample_text)
        
        print("\n--- Atomic Claims (Mocked) ---")
        for i, claim in enumerate(claims, 1):
            print(f"{i}. {claim}")
            
        # Assertion
        assert len(claims) == 3
        assert "1890" in claims[0]
        print("\nSUCCESS: Analyzer logic verified (JSON parsing and object mapping works).")

if __name__ == "__main__":
    asyncio.run(main())
