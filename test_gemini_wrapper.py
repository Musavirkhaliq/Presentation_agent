"""
Test script for the updated LLM wrapper with Gemini.
"""
import os
from src.utils.llm_wrapper import LLMWrapper
from dotenv import load_dotenv

def main():
    """
    Test the updated LLM wrapper with Gemini.
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key from environment variable
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("No API key found. Please set the GEMINI_API_KEY environment variable.")
        return

    # Test with gemini-2.0-flash model
    print("\nTesting with gemini-2.0-flash model:")
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
    
    structured_response = llm.generate_structured(
        prompt="Explain how AI works in a few words",
        output_schema=schema,
        temperature=0.7
    )
    print(f"Structured Response: {structured_response}")
    
    # Test with system prompt
    print("\nTesting with system prompt:")
    response = llm.generate(
        prompt="What are you?",
        system_prompt="You are a helpful AI assistant that provides concise answers.",
        temperature=0.7,
        max_tokens=1000
    )
    print(f"Response with system prompt: {response}")

if __name__ == "__main__":
    main()
