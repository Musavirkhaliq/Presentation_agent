"""
Test script for the LLM wrapper.
"""
import os
from src.utils.llm_wrapper import LLMWrapper

def main():
    """
    Test the LLM wrapper with Gemini.
    """
    # Get API key from environment variable
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("No API key found. Please set the GEMINI_API_KEY environment variable.")
        return

    # Initialize the LLM wrapper
    llm = LLMWrapper(model="gemini-2.0-flash", api_key=api_key, provider="gemini")
    
    # Test simple text generation
    print("\nTesting simple text generation:")
    response = llm.generate(
        prompt="Explain how AI works in a few words",
        temperature=0.7,
        max_tokens=1000
    )
    print(f"Response: {response}")
    
    # Test structured output generation
    print("\nTesting structured output generation:")
    schema = {
        "type": "object",
        "properties": {
            "explanation": {"type": "string"},
            "key_points": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["explanation", "key_points"]
    }
    
    response = llm.generate_structured(
        prompt="Explain how AI works in a few words",
        output_schema=schema,
        temperature=0.7
    )
    print(f"Response: {response}")

if __name__ == "__main__":
    main()
