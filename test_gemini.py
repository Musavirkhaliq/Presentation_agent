import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY environment variable not set.")
    exit(1)

print(f"Using API key: {api_key[:4]}...{api_key[-4:]}")

try:
    # Configure the Gemini API
    genai.configure(api_key=api_key)

    # Try to use the gemini-1.5-flash model
    print("\nTesting gemini-1.5-flash model:")
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Hello, what's the current date?")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error with gemini-1.5-flash: {str(e)}")

    # Try to use the gemini-2.0-flash model
    print("\nTesting gemini-2.0-flash model:")
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content("Hello, what's the current date?")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error with gemini-2.0-flash: {str(e)}")

    # Try to use the gemini-pro model as a fallback
    print("\nTesting gemini-pro model:")
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content("Hello, what's the current date?")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error with gemini-pro: {str(e)}")

except Exception as e:
    print(f"General error: {str(e)}")
