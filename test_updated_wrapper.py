"""
Test script for the updated LLM wrapper.
"""
import os
from src.utils.llm_wrapper import LLMWrapper

def main():
    """
    Test the updated LLM wrapper.
    """
    # Get API key from environment variable
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("No API key found. Please set the GEMINI_API_KEY environment variable.")
        return

    # Test with gemini-2.0-flash model
    print("\nTesting with gemini-2.0-flash model:")
    llm = LLMWrapper(model="gemini-2.0-flash", api_key=api_key)
    response = llm.generate(
        prompt="Explain how AI works in a few words",
        temperature=0.7,
        max_tokens=1000
    )
    print(f"Response: {response}")
    
    # Test with gemini-1.5-flash model
    print("\nTesting with gemini-1.5-flash model:")
    llm = LLMWrapper(model="gemini-1.5-flash", api_key=api_key)
    response = llm.generate(
        prompt="Explain how AI works in a few words",
        temperature=0.7,
        max_tokens=1000
    )
    print(f"Response: {response}")
    
    # Test structured output
    print("\nTesting structured output:")
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
