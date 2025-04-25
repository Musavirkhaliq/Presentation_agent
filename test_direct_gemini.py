"""
Test script for directly using the Google Generative AI library with the new API.
"""
import os
from dotenv import load_dotenv

def main():
    """
    Test the Google Generative AI library with gemini-2.0-flash.
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key from environment variable
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("No API key found. Please set the GEMINI_API_KEY environment variable.")
        return

    print(f"Using API key: {api_key[:4]}...{api_key[-4:]}")

    try:
        # Import the library
        from google import genai
        
        # Initialize the client
        client = genai.Client(api_key=api_key)
        
        # Test with gemini-2.0-flash model
        print("\nTesting gemini-2.0-flash model:")
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents="Explain how AI works in a few words"
        )
        print(f"Response: {response.text}")
        
        # Test with gemini-1.5-flash model
        print("\nTesting gemini-1.5-flash model:")
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents="Explain how AI works in a few words"
        )
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
