"""
Main entry point for the Presentation Maker application.
"""
import os
import argparse
from typing import Optional
from src.presentation_maker import PresentationMaker
from src.utils.presentation_utils import PresentationFormat

def read_file(file_path: str) -> Optional[str]:
    """
    Read content from a file.

    Args:
        file_path: Path to the file

    Returns:
        File content or None if file doesn't exist
    """
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def main():
    """
    Main function to run the presentation maker.
    """
    parser = argparse.ArgumentParser(description="Create presentations from input material")
    parser.add_argument("--input", "-i", type=str, help="Input material file path")
    parser.add_argument("--output", "-o", type=str, default="presentation", help="Output file path")
    parser.add_argument("--format", "-f", type=str, choices=["markdown", "html"], default="markdown",
                        help="Output format (markdown or html)")
    parser.add_argument("--model", "-m", type=str, default="gemini-2.0-flash", help="LLM model to use (e.g., gemini-2.0-flash, gemini-1.5-flash)")
    parser.add_argument("--provider", "-p", type=str, choices=["gemini", "openai"], default="gemini", help="LLM provider to use")
    parser.add_argument("--outline-only", action="store_true", help="Generate only the outline")
    parser.add_argument("--material", type=str, help="Direct input material (alternative to --input)")
    parser.add_argument("--api-key", type=str, help="API key for the LLM provider")

    args = parser.parse_args()

    # Get the input material
    material = None
    if args.input:
        material = read_file(args.input)
        if not material:
            return
    elif args.material:
        material = args.material
    else:
        print("Error: No input material provided. Use --input or --material")
        return

    # Set the format
    format_type = PresentationFormat.MARKDOWN if args.format == "markdown" else PresentationFormat.HTML

    # Create the presentation maker
    presentation_maker = PresentationMaker(
        model=args.model,
        api_key=args.api_key,
        provider=args.provider,
        format_type=format_type
    )

    # Generate the presentation or outline
    if args.outline_only:
        print("Generating presentation outline...")
        result = presentation_maker.get_outline(material)

        if "error" in result:
            print(f"Error: {result['error']}")
            return

        outline = result
        print("\n=== Presentation Outline ===\n")
        print(f"Title: {outline.get('title', 'No title generated')}\n")

        for i, slide in enumerate(outline.get("slides", [])):
            print(f"Slide {i+1}: {slide.get('title', 'No title')}")
            for point in slide.get("key_points", []):
                print(f"  - {point}")
            print()
    else:
        output_file = args.output
        if not output_file.endswith(".md") and not output_file.endswith(".html"):
            extension = ".md" if format_type == PresentationFormat.MARKDOWN else ".html"
            output_file += extension

        print(f"Creating presentation from input material...")
        result = presentation_maker.create_presentation(material, output_file)

        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"\nPresentation created successfully!")
            if "presentation" in result:
                print(f"Title: {result['presentation']['title']}")
            print(f"Saved to: {result.get('saved_file', output_file)}")
            print(f"Format: {args.format}")
            if "slides" in result:
                print(f"\nThe presentation contains {len(result['slides'])} slides.")

if __name__ == "__main__":
    main()
