import asyncio
import json
import os
from typing import List, Optional

from litellm import acompletion
from pydantic import BaseModel, Field

# Define Pydantic models for structured output
class AtomicFact(BaseModel):
    fact: str = Field(..., description="A single, atomic, verifiable fact extracted from the text.")

class ExtractionResponse(BaseModel):
    facts: List[AtomicFact] = Field(..., description="List of extracted atomic facts.")

class BackstoryAnalyzer:
    """
    Analyzes and decomposes complex backstories into atomic facts/claims.
    """

    def __init__(self, llm_config: dict = None):
        """
        Initialize the analyzer with LLM configuration.

        Args:
            llm_config (dict): Configuration for the LLM. 
                               Defaults to using 'gemini-1.5-pro' compatible settings.
        """
        self.llm_config = llm_config or {}
        self.model_name = self.llm_config.get("model", "gemini/gemini-1.5-pro-latest")
        # Prefer specific key in config, else check common env vars, else let litellm handle it
        self.api_key = self.llm_config.get("api_key") 
        if not self.api_key:
             # Fallback check for Gemini/OpenAI/XAI for convenience, though Litellm does this too
             self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("XAI_API_KEY") or os.getenv("OPENAI_API_KEY")

    async def extract_atomic_claims(self, backstory: str) -> List[str]:
        """
        Decomposes a backstory into atomic, verifiable facts.
        
        Process:
        1. Extraction: LLM breaks text into facts (preserving entities/dates).
        2. Self-Correction: LLM reviews facts against original text.

        Args:
            backstory (str): The narrative text to analyze.

        Returns:
            List[str]: A list of verified atomic strings.
        """
        if not backstory or not backstory.strip():
            return []

        # Step 1: Extraction
        raw_claims = await self._decompose_text(backstory)
        
        # Step 2: Self-Correction/Validation
        validated_claims = await self._validate_claims(backstory, raw_claims)
        
        return validated_claims

    async def _decompose_text(self, text: str) -> List[str]:
        """
        Internal method to perform the initial decomposition.
        """
        prompt = f"""
        You are an expert Forensic Narrative Analyst.
        Target: Break the following text into a list of ATOMIC, VERIFIABLE facts.
        
        Rules:
        1. Each fact must be a single standalone sentence.
        2. Preserve ALL specific details: Dates, Names, Locations, Relationships.
        3. Do not summarize; decompose.
        4. "The library burned in 1995" -> "The library burned." AND "The fire occurred in 1995." (Better: "The library burned in 1995" is atomic enough if verified together, but split complex compound sentences).
        5. Output strictly valid JSON matching the schema: {{ "facts": [ {{ "fact": "..." }}, ... ] }}

        Text:
        "{text}"
        """
        
        try:
            response = await acompletion(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                api_key=self.api_key
            )
            
            content = response.choices[0].message.content
            parsed = ExtractionResponse.model_validate_json(content)
            return [item.fact for item in parsed.facts]
        except Exception as e:
            print(f"Extraction error: {e}")
            # Fallback for demo purposes or robustness
            return [text]

    async def _validate_claims(self, original_text: str, claims: List[str]) -> List[str]:
        """
        Internal method to validate/correct the extracted claims.
        """
        if not claims:
            return []

        prompt = f"""
        Review the following list of extracted claims against the original text.
        
        Original Text:
        "{original_text}"
        
        Extracted Claims:
        {json.dumps(claims, indent=2)}
        
        Task:
        1. Remove any claims that are NOT supported by the text (hallucinations).
        2. Correct any claims that distort the original meaning.
        3. Return the final filtered list of atomic facts.
        4. Output strictly valid JSON: {{ "facts": [ {{ "fact": "..." }}, ... ] }}
        """

        try:
            response = await acompletion(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                api_key=self.api_key
            )
            
            content = response.choices[0].message.content
            parsed = ExtractionResponse.model_validate_json(content)
            return [item.fact for item in parsed.facts]
        except Exception as e:
            print(f"Validation error: {e}")
            return claims
