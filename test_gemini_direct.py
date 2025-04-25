"""
Test script for directly using the Google Generative AI library.
"""
import os
import google.generativeai as genai

def main():
    """
    Test the Google Generative AI library with gemini-2.0-flash.
    """
    # Get API key from environment variable
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("No API key found. Please set the GEMINI_API_KEY environment variable.")
        return

    # Configure the API
    genai.configure(api_key=api_key)

    # Test with gemini-1.5-flash model
    try:
        print("\nTesting gemini-1.5-flash model:")
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Explain how AI works in a few words")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error with gemini-1.5-flash: {str(e)}")

    # Test with gemini-pro model
    try:
        print("\nTesting gemini-pro model:")
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content("Explain how AI works in a few words")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error with gemini-pro: {str(e)}")

    # Test with gemini-2.0-flash model
    try:
        print("\nTesting gemini-2.0-flash model:")
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content("Explain how AI works in a few words")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error with gemini-2.0-flash: {str(e)}")

if __name__ == "__main__":
    main()
