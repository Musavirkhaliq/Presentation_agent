"""
Image Finder Node for finding and adding images to slides.
"""
from typing import Dict, Any, List, Optional
import os
from pocketflow import Node
from src.utils.image_utils import ImageUtils

class ImageFinder(Node):
    """
    Node for finding relevant images for slides based on their content.
    """

    def __init__(self, llm_wrapper, max_retries=1, images_dir="images"):
        """
        Initialize the image finder node.

        Args:
            llm_wrapper: LLM wrapper for making API calls
            max_retries: Maximum number of retries for LLM calls
            images_dir: Directory to save downloaded images
        """
        super().__init__(max_retries=max_retries)
        self.llm_wrapper = llm_wrapper
        self.images_dir = images_dir
        
        # Create the images directory if it doesn't exist
        os.makedirs(self.images_dir, exist_ok=True)

    def prep(self, shared):
        """
        Prepare the slides for image finding.

        Args:
            shared: Shared state dictionary

        Returns:
            Dictionary with slides and system prompt
        """
        slides = shared.get("slides", [])

        if not slides:
            return {"error": "No slides available for image finding"}

        system_prompt = """
        You are an expert at creating search queries for finding relevant images.
        Your task is to create concise, specific search queries that will return
        high-quality, professional images suitable for presentation slides.
        """

        return {
            "slides": slides,
            "system_prompt": system_prompt
        }

    def exec(self, prep_res):
        """
        Execute the image finding for each slide.

        Args:
            prep_res: Result from prep step

        Returns:
            List of slides with added images
        """
        if "error" in prep_res:
            return {"error": prep_res["error"]}

        slides = prep_res["slides"]
        system_prompt = prep_res["system_prompt"]
        
        slides_with_images = []

        for slide in slides:
            slide_title = slide["title"]
            slide_content = slide["content"]
            
            # Generate search query based on slide content
            base_query = ImageUtils.generate_image_search_query(slide_title, slide_content)
            
            prompt = f"""
            Create a specific image search query for a slide with the title: "{slide_title}"
            
            The slide content is:
            {slide_content}
            
            Based on this content, create a concise search query that will find
            a professional, relevant image for this slide. The query should be
            specific enough to find images that represent the key concepts of the slide.
            
            Return ONLY the search query, nothing else.
            """
            
            # Generate the search query using LLM
            search_query = self.llm_wrapper.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=100
            )
            
            # Clean up the search query
            search_query = search_query.strip().replace('"', '').replace("'", "")
            
            # If the LLM returned a long response, use the base query instead
            if len(search_query.split()) > 10 or len(search_query) < 3:
                search_query = base_query
                
            print(f"Searching for images for slide: {slide_title}")
            print(f"Search query: {search_query}")
            
            # Search for images
            image_urls = ImageUtils.search_images(search_query, per_page=3)
            
            if image_urls:
                # Use the first image found
                image_url = image_urls[0]
                
                # Download and save the image
                image_path = ImageUtils.download_image(image_url, self.images_dir)
                
                if image_path:
                    # Use relative path for markdown
                    relative_path = os.path.relpath(image_path, os.getcwd())
                    
                    # Add the image to the slide
                    slide_content = ImageUtils.add_image_to_slide_markdown(
                        slide_content, 
                        relative_path, 
                        f"Illustration for {slide_title}"
                    )
                    
                    # Update the slide content
                    slide["content"] = slide_content
                    slide["image_path"] = relative_path
                    print(f"Added image to slide: {slide_title}")
                else:
                    print(f"Failed to download image for slide: {slide_title}")
            else:
                print(f"No images found for slide: {slide_title}")
            
            slides_with_images.append(slide)

        return slides_with_images

    def post(self, shared, prep_res, exec_res):
        """
        Update the shared state with the slides with images.

        Args:
            shared: Shared state dictionary
            prep_res: Result from prep step
            exec_res: Result from exec step

        Returns:
            Action string for flow control
        """
        if isinstance(exec_res, dict) and "error" in exec_res:
            shared["error"] = exec_res["error"]
            return "error"

        # Update the shared state with the slides with images
        shared["slides"] = exec_res

        # Return default action
        return "default"
