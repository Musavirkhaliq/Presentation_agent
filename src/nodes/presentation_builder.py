"""
Presentation Builder Node for assembling the final presentation.
"""
from typing import Dict, Any, List, Optional
from pocketflow import Node
from src.utils.presentation_utils import PresentationUtils, PresentationFormat

class PresentationBuilder(Node):
    """
    Node for assembling the final presentation from individual slides.
    """

    def __init__(self, format_type=PresentationFormat.MARKDOWN, max_retries=1):
        """
        Initialize the presentation builder node.

        Args:
            format_type: The format to use for the presentation
            max_retries: Maximum number of retries
        """
        super().__init__(max_retries=max_retries)
        self.format_type = format_type

    def prep(self, shared):
        """
        Prepare the slides and outline for presentation building.

        Args:
            shared: Shared state dictionary

        Returns:
            Dictionary with slides, title, and format type
        """
        slides = shared.get("slides", [])
        outline = shared.get("outline", {})

        if not slides:
            return {"error": "No slides available to build presentation"}

        title = outline.get("title", "Presentation")

        return {
            "slides": slides,
            "title": title,
            "format_type": self.format_type
        }

    def exec(self, prep_res):
        """
        Execute the presentation building process.

        Args:
            prep_res: Result from prep step

        Returns:
            Dictionary with presentation details
        """
        if "error" in prep_res:
            return {"error": prep_res["error"]}

        slides = prep_res["slides"]
        title = prep_res["title"]
        format_type = prep_res["format_type"]

        # Build the presentation based on the format type
        if format_type == PresentationFormat.MARKDOWN:
            presentation = PresentationUtils.create_presentation_markdown(slides, title)
        else:  # HTML format
            presentation = PresentationUtils.create_presentation_html(slides, title)

        return {
            "title": title,
            "content": presentation,
            "format": format_type
        }

    def post(self, shared, prep_res, exec_res):
        """
        Update the shared state with the final presentation.

        Args:
            shared: Shared state dictionary
            prep_res: Result from prep step
            exec_res: Result from exec step

        Returns:
            Action string for flow control
        """
        if "error" in exec_res:
            shared["error"] = exec_res["error"]
            return "error"

        # Update the shared state with the final presentation
        shared["presentation"] = exec_res

        # Return default action
        return "default"
