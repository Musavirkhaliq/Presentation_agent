"""
Example of using the presentation maker with image finding.
"""
import os
import sys
from src.presentation_maker import PresentationMaker
from src.utils.presentation_utils import PresentationFormat

def main():
    """
    Main function to demonstrate using the presentation maker with image finding.
    """
    # Check if API key is provided
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    provider = "gemini" if os.environ.get("GEMINI_API_KEY") else "openai"

    if not api_key:
        print("Error: No API key found. Please set either GEMINI_API_KEY or OPENAI_API_KEY environment variable.")
        print("For Gemini: export GEMINI_API_KEY=your_api_key_here")
        print("For OpenAI: export OPENAI_API_KEY=your_api_key_here")
        return

    # Sample material for the presentation
    material = """
    Artificial Intelligence (AI) is transforming our world in unprecedented ways.

    The history of AI dates back to the 1950s when the term was first coined. Early AI
    focused on symbolic approaches and rule-based systems. The AI winter in the 1970s and
    1980s slowed progress due to limited computing power and data.

    The current AI landscape is dominated by deep learning, a subset of machine learning using
    neural networks with multiple layers. This approach has led to breakthroughs in computer
    vision, natural language processing, and reinforcement learning.

    The future of AI presents both opportunities and challenges, including healthcare applications,
    climate change solutions, ethical concerns, and the potential development of Artificial
    General Intelligence (AGI).
    """

    # Create the presentation maker
    presentation_maker = PresentationMaker(
        model="gemini-1.5-flash" if provider == "gemini" else "gpt-4",
        api_key=api_key,
        provider=provider,
        format_type=PresentationFormat.MARKDOWN
    )

    # Generate the full presentation with images
    print(f"Creating presentation with {provider.capitalize()} including images from the web...")
    result = presentation_maker.create_presentation(material, f"ai_presentation_with_images_{provider}.md")

    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"\nPresentation created successfully!")
        if "presentation" in result:
            print(f"Title: {result['presentation']['title']}")
        print(f"Saved to: {result.get('saved_file', f'ai_presentation_with_images_{provider}.md')}")
        print(f"\nThe presentation contains {len(result.get('slides', []))} slides with images.")

if __name__ == "__main__":
    main()
