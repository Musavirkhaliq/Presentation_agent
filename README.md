# Presentation Maker Agent

A PocketFlow-based agent that creates presentations from input material. The agent reads the provided material, generates an outline, creates slides, and builds a complete presentation.

## Features

- Process input material to extract key information
- Generate a structured outline for the presentation
- Create individual slides with engaging content
- Build a complete presentation in Markdown or HTML format
- Support for reviewing the outline before creating the full presentation
- Support for multiple LLM providers (Gemini and OpenAI)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/presentation-maker.git
cd presentation-maker
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

Create a presentation from a file using Gemini (default):

```bash
python -m src.main --input input_material.txt --output my_presentation --format markdown
```

Create a presentation using OpenAI:

```bash
python -m src.main --input input_material.txt --provider openai --model gpt-4 --output my_presentation
```

Create a presentation from direct input:

```bash
python -m src.main --material "Your input material here..." --output my_presentation
```

Generate only the outline:

```bash
python -m src.main --input input_material.txt --outline-only
```

### Options

- `--input`, `-i`: Input material file path
- `--output`, `-o`: Output file path (default: "presentation")
- `--format`, `-f`: Output format (markdown or html, default: markdown)
- `--model`, `-m`: LLM model to use (default: gemini-1.5-flash)
- `--provider`, `-p`: LLM provider to use (gemini or openai, default: gemini)
- `--outline-only`: Generate only the outline
- `--material`: Direct input material (alternative to --input)
- `--api-key`: API key for the LLM provider (alternatively, use environment variables)

### Environment Variables

- For Gemini: Set `GEMINI_API_KEY` environment variable
- For OpenAI: Set `OPENAI_API_KEY` environment variable

You can set these environment variables in your shell or create a `.env` file in the project root directory:

```
# .env file
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

The application will automatically load environment variables from the `.env` file.

### Gemini API Key and Models

To get a Gemini API key:

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an account or sign in
3. Create a new API key
4. Copy the API key and add it to your `.env` file or set it as an environment variable

Supported Gemini models:
- `gemini-1.5-flash` (default): Fast and efficient model for most use cases
- `gemini-1.5-pro`: More powerful model for complex tasks
- `gemini-pro`: Original Gemini model
- `gemini-1.0-pro`: Legacy model

Note: If you encounter errors with the Gemini API, the application will automatically fall back to a mock implementation for testing purposes. This can happen if your API key doesn't have access to the specified model or if there are connectivity issues.

## Using as a Library

You can also use the Presentation Maker as a library in your own Python code:

```python
from src.presentation_maker import PresentationMaker
from src.utils.presentation_utils import PresentationFormat

# Create a presentation maker with Gemini
presentation_maker = PresentationMaker(
    model="gemini-1.5-flash",
    api_key="your_gemini_api_key",  # Or set GEMINI_API_KEY env variable
    provider="gemini",
    format_type=PresentationFormat.MARKDOWN
)

# Or create a presentation maker with OpenAI
presentation_maker = PresentationMaker(
    model="gpt-4",
    api_key="your_openai_api_key",  # Or set OPENAI_API_KEY env variable
    provider="openai",
    format_type=PresentationFormat.MARKDOWN
)

# Generate a presentation
material = "Your input material here..."
result = presentation_maker.create_presentation(material, "my_presentation.md")

# Or just get the outline
outline = presentation_maker.get_outline(material)
```

## Example

See `examples/use_gemini.py` for a complete example of using the presentation maker with Gemini.

## Requirements

- Python 3.7+
- PocketFlow
- For Gemini: Google Generative AI package (`pip install google-generativeai`)
- For OpenAI: OpenAI package (`pip install openai`)

## License

MIT
