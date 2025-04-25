"""
Test script for the OutlineGenerator node with the updated LLM wrapper.
"""
import os
from src.utils.llm_wrapper import LLMWrapper
from src.nodes.outline_generator import OutlineGenerator
from dotenv import load_dotenv

def main():
    """
    Test the OutlineGenerator node with the updated LLM wrapper.
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key from environment variable
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("No API key found. Please set the GEMINI_API_KEY environment variable.")
        return

    # Initialize the LLM wrapper
    llm = LLMWrapper(model="gemini-2.0-flash", api_key=api_key, provider="gemini")
    
    # Initialize the OutlineGenerator node
    outline_generator = OutlineGenerator(llm_wrapper=llm)
    
    # Sample processed material
    processed_material = """
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
    
    # Create a shared state dictionary
    shared = {"processed_material": processed_material}
    
    # Run the prep step
    print("Running prep step...")
    prep_res = outline_generator.prep(shared)
    
    # Run the exec step
    print("\nRunning exec step...")
    exec_res = outline_generator.exec(prep_res)
    
    # Print the result
    print("\nOutline result:")
    if "error" in exec_res:
        print(f"Error: {exec_res['error']}")
    else:
        print(f"Title: {exec_res.get('title', 'No title generated')}\n")
        for i, slide in enumerate(exec_res.get("slides", [])):
            print(f"Slide {i+1}: {slide.get('title', 'No title')}")
            for point in slide.get("key_points", []):
                print(f"  - {point}")
            print()
    
    # Run the post step
    print("Running post step...")
    post_res = outline_generator.post(shared, prep_res, exec_res)
    print(f"Post result: {post_res}")
    
    # Print the updated shared state
    print("\nUpdated shared state:")
    if "outline" in shared:
        print(f"Outline title: {shared['outline'].get('title', 'No title')}")
        print(f"Number of slides: {len(shared['outline'].get('slides', []))}")
    else:
        print("No outline in shared state")

if __name__ == "__main__":
    main()
