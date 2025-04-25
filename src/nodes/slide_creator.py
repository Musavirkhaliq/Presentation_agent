"""
Slide Creator Node for creating individual slides.
"""
from typing import Dict, Any, List, Optional
from pocketflow import Node

class SlideCreator(Node):
    """
    Node for creating individual slides based on the outline.
    """

    def __init__(self, llm_wrapper, max_retries=1):
        """
        Initialize the slide creator node.

        Args:
            llm_wrapper: LLM wrapper for making API calls
            max_retries: Maximum number of retries for LLM calls
        """
        super().__init__(max_retries=max_retries)
        self.llm_wrapper = llm_wrapper

    def prep(self, shared):
        """
        Prepare the outline and processed material for slide creation.

        Args:
            shared: Shared state dictionary

        Returns:
            Dictionary with outline, processed material, and system prompt
        """
        outline = shared.get("outline", {})
        processed_material = shared.get("processed_material", "")

        if not outline or "slides" not in outline:
            return {"error": "No valid outline available"}

        system_prompt = """
        You are an expert presentation designer who creates engaging, visually appealing,
        and informative slides. Each slide should be concise yet comprehensive, with clear
        formatting and a good balance of text and visual cues.
        """

        return {
            "outline": outline,
            "processed_material": processed_material,
            "system_prompt": system_prompt
        }

    def exec(self, prep_res):
        """
        Execute the LLM calls to create slides for each outline item.

        Args:
            prep_res: Result from prep step

        Returns:
            List of created slides
        """
        if "error" in prep_res:
            return {"error": prep_res["error"]}

        outline = prep_res["outline"]
        processed_material = prep_res["processed_material"]
        system_prompt = prep_res["system_prompt"]

        slides = []

        # Create each slide based on the outline
        for slide_outline in outline["slides"]:
            slide_title = slide_outline["title"]
            key_points = slide_outline["key_points"]

            prompt = f"""
            Create the content for a presentation slide with the title "{slide_title}".

            The slide should cover these key points:
            {', '.join(key_points)}

            Based on this information from the processed material:
            {processed_material}

            Create engaging slide content that:
            1. Is concise but informative
            2. Uses bullet points where appropriate
            3. Includes any relevant examples or data points
            4. Is formatted for easy reading (use markdown formatting)
            5. Balances text with suggestions for visuals

            Format your response as markdown content that would appear on the slide.
            Do not include the slide title in your response.
            """

            slide_content = self.llm_wrapper.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=1000
            )

            slides.append({
                "title": slide_title,
                "content": slide_content
            })

        return slides

    def post(self, shared, prep_res, exec_res):
        """
        Update the shared state with the created slides.

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

        # Update the shared state with the created slides
        shared["slides"] = exec_res

        # Return default action
        return "default"
