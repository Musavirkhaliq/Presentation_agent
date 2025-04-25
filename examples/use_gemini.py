"""
Example of using the presentation maker with Gemini.
"""
import os
import sys
from src.presentation_maker import PresentationMaker
from src.utils.presentation_utils import PresentationFormat

def main():
    """
    Main function to demonstrate using the presentation maker with Gemini.
    """
    # Check if Gemini API key is provided
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        print("Please set your Gemini API key with:")
        print("export GEMINI_API_KEY=your_api_key_here")
        return

    # Sample material
    material = """
    Artificial Intelligence: Past, Present, and Future

    Artificial Intelligence (AI) has evolved significantly since its inception in the 1950s.
    Initially, AI research focused on symbolic reasoning and rule-based systems. Early AI
    systems like ELIZA, a simple chatbot created in the 1960s, demonstrated basic natural
    language processing capabilities but lacked true understanding.

    The field experienced several "AI winters" - periods of reduced funding and interest due
    to unmet expectations. However, the late 1990s and early 2000s saw renewed interest with
    the development of machine learning approaches that could learn from data rather than
    following explicit programming.

    The current AI landscape is dominated by deep learning, a subset of machine learning using
    neural networks with multiple layers. This approach has led to breakthroughs in computer
    vision, natural language processing, and reinforcement learning.

    The future of AI presents both opportunities and challenges, including healthcare applications,
    climate change solutions, ethical concerns, and the potential development of Artificial
    General Intelligence (AGI).
    """

    # Create the presentation maker with Gemini
    presentation_maker = PresentationMaker(
        model="gemini-1.5-flash",
        api_key=gemini_api_key,
        provider="gemini",
        format_type=PresentationFormat.MARKDOWN
    )

    # Generate the outline
    print("Generating presentation outline...")
    outline = presentation_maker.get_outline(material)

    # Print the outline
    print("\n=== Presentation Outline ===\n")
    print(f"Title: {outline.get('title', 'No title generated')}\n")

    for i, slide in enumerate(outline.get("slides", [])):
        print(f"Slide {i+1}: {slide.get('title', 'No title')}")
        for point in slide.get("key_points", []):
            print(f"  - {point}")
        print()

    # Generate the full presentation
    print("Creating full presentation...")
    result = presentation_maker.create_presentation(material, "ai_presentation_gemini.md")

    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"\nPresentation created successfully!")
        if "presentation" in result:
            print(f"Title: {result['presentation']['title']}")
        print(f"Saved to: {result.get('saved_file', 'ai_presentation_gemini.md')}")
        print(f"\nThe presentation contains {len(result.get('slides', []))} slides.")

if __name__ == "__main__":
    main()
