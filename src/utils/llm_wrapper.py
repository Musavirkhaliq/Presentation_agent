"""
LLM Wrapper for making API calls to language models.
"""
import os
import json
import random
from typing import Dict, List, Optional, Union, Any
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Try to load from .env file in the current directory
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)
    # Also try to load from the project root directory
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    print("python-dotenv not installed. Environment variables will not be loaded from .env file.")
    print("Install with: pip install python-dotenv")

class MockLLM:
    """
    A mock LLM client for testing without API keys.
    """
    def __init__(self):
        self.chat = self.ChatCompletions()

    class ChatCompletions:
        def create(self, model, messages, temperature=0.7, max_tokens=1000, response_format=None):
            """Mock create method"""
            class MockResponse:
                class Message:
                    def __init__(self, content):
                        self.content = content

                class Choice:
                    def __init__(self, message):
                        self.message = message

                def __init__(self, content):
                    self.choices = [self.Choice(self.Message(content))]

            # If response format is JSON, return a simple JSON structure
            if response_format and response_format.get("type") == "json_object":
                if "outline" in str(messages):
                    return MockResponse(json.dumps({
                        "title": "Sample Presentation",
                        "slides": [
                            {
                                "title": "Introduction",
                                "key_points": ["Point 1", "Point 2", "Point 3"]
                            },
                            {
                                "title": "Main Content",
                                "key_points": ["Point A", "Point B", "Point C"]
                            },
                            {
                                "title": "Conclusion",
                                "key_points": ["Summary 1", "Summary 2", "Call to action"]
                            }
                        ]
                    }))
                else:
                    return MockResponse(json.dumps({"result": "This is a mock JSON response"}))

            # For regular text responses
            prompt = messages[-1]["content"] if messages else ""
            if "outline" in prompt:
                return MockResponse("This is a mock outline response.")
            elif "slide" in prompt:
                return MockResponse("This is mock slide content with bullet points:\n- Point 1\n- Point 2\n- Point 3")
            else:
                return MockResponse("This is a mock response from the LLM.")

class GeminiClient:
    """
    A client for Google's Gemini API using the new google.genai library.
    """
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = None
        self.chat = self.ChatCompletions(self)

        try:
            # Use the updated import syntax
            from google import genai
            # Initialize the client with the new API
            self.client = genai.Client(api_key=self.api_key)
        except ImportError:
            print("Google Generative AI package not installed. Please install it with 'pip install google-generativeai'")

    class ChatCompletions:
        def __init__(self, client):
            self.client = client

        def create(self, model, messages, temperature=0.7, max_tokens=1000, response_format=None):
            """Create a chat completion using Gemini."""
            class GeminiResponse:
                class Message:
                    def __init__(self, content):
                        self.content = content

                class Choice:
                    def __init__(self, message):
                        self.message = message

                def __init__(self, content):
                    self.choices = [self.Choice(self.Message(content))]

            if not self.client.client:
                return GeminiResponse("Error: Google Generative AI not initialized")

            # Process messages to extract content
            prompt = ""
            system_prompt = ""

            for msg in messages:
                if msg["role"] == "system":
                    system_prompt = msg["content"]
                elif msg["role"] == "user":
                    prompt = msg["content"]

            # Combine system prompt and user prompt if both exist
            if system_prompt and prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            else:
                full_prompt = prompt or system_prompt

            # Handle JSON response format
            if response_format and response_format.get("type") == "json_object":
                full_prompt = f"{full_prompt}\n\nYou must respond with a valid JSON object only."

            try:
                # Use the direct API approach that we know works
                response = self.client.client.models.generate_content(
                    model=model,
                    contents=full_prompt
                )

                return GeminiResponse(response.text)
            except Exception as e:
                return GeminiResponse(f"Error generating content: {str(e)}")

class LLMWrapper:
    """
    A wrapper for making calls to language model APIs.
    """

    def __init__(self, model: str = "gemini-2.0-flash", api_key: Optional[str] = None, provider: str = "gemini"):
        """
        Initialize the LLM wrapper.

        Args:
            model: The model to use for generation
            api_key: API key for the LLM provider (defaults to env variable)
            provider: The LLM provider to use (gemini or openai)
        """
        self.model = model
        self.provider = provider.lower()
        self.use_mock = False

        # Set up the client based on the provider
        if self.provider == "gemini":
            self.api_key = api_key or os.environ.get("GEMINI_API_KEY")

            if not self.api_key:
                print("Warning: No Gemini API key found. Using mock implementation.")
                self.client = MockLLM()
                self.use_mock = True
            else:
                print(f"Using Gemini API key: {self.api_key[:4]}...{self.api_key[-4:] if len(self.api_key) > 8 else ''}")
                try:
                    self.client = GeminiClient(api_key=self.api_key)
                except Exception as e:
                    print(f"Error initializing Gemini client: {str(e)}. Using mock implementation.")
                    self.client = MockLLM()
                    self.use_mock = True
        else:  # OpenAI
            self.api_key = api_key or os.environ.get("OPENAI_API_KEY")

            try:
                import openai
                if not self.api_key:
                    print("Warning: No OpenAI API key found. Using mock implementation.")
                    self.client = MockLLM()
                    self.use_mock = True
                else:
                    self.client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                print("OpenAI package not installed. Using mock implementation.")
                self.client = MockLLM()
                self.use_mock = True

    def generate(self,
                prompt: str,
                system_prompt: Optional[str] = None,
                temperature: float = 0.7,
                max_tokens: int = 1000) -> str:
        """
        Generate text using the language model.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            temperature: Controls randomness (0-1)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        if not self.client:
            return "Error: LLM client not initialized"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            # For Gemini, use the chat.create method directly
            if self.provider == "gemini":
                response = self.client.chat.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            else:  # OpenAI
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating text: {str(e)}"

    def generate_structured(self,
                           prompt: str,
                           output_schema: Dict[str, Any],
                           system_prompt: Optional[str] = None,
                           temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate structured output using the language model.

        Args:
            prompt: The user prompt
            output_schema: JSON schema for the expected output
            system_prompt: Optional system prompt
            temperature: Controls randomness (0-1)

        Returns:
            Structured output as a dictionary
        """
        if not self.client:
            return {"error": "LLM client not initialized"}

        schema_prompt = f"""
        You must respond with a JSON object that conforms to this schema:
        {json.dumps(output_schema, indent=2)}

        Your response should be valid JSON that can be parsed by json.loads().
        """

        full_prompt = f"{schema_prompt}\n\n{prompt}"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": full_prompt})

        try:
            # For Gemini, we handle JSON formatting in the prompt
            if self.provider == "gemini":
                response = self.client.chat.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=1000  # Default max tokens for structured output
                )
            else:  # OpenAI
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    response_format={"type": "json_object"}
                )

            result = response.choices[0].message.content

            # Clean the result for Gemini responses
            if self.provider == "gemini":
                # Remove markdown code blocks if present
                if result.startswith("```json") and result.endswith("```"):
                    result = result[7:-3].strip()
                elif result.startswith("```") and result.endswith("```"):
                    result = result[3:-3].strip()

            return json.loads(result)
        except json.JSONDecodeError as e:
            return {"error": f"Error parsing JSON response: {str(e)}", "raw_response": result}
        except Exception as e:
            return {"error": f"Error generating structured output: {str(e)}"}