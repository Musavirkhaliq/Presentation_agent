"""
Outline Generator Node for creating presentation outlines.
"""
from typing import Dict, Any, List, Optional
import json
from pocketflow import Node

class OutlineGenerator(Node):
    """
    Node for generating presentation outlines from processed material.
    """

    def __init__(self, llm_wrapper, max_retries=1):
        """
        Initialize the outline generator node.

        Args:
            llm_wrapper: LLM wrapper for making API calls
            max_retries: Maximum number of retries for LLM calls
        """
        super().__init__(max_retries=max_retries)
        self.llm_wrapper = llm_wrapper

    def prep(self, shared):
        """
        Prepare the processed material for outline generation.

        Args:
            shared: Shared state dictionary

        Returns:
            Dictionary with processed material and prompts
        """
        processed_material = shared.get("processed_material", "")
        if not processed_material:
            return {"error": "No processed material available"}

        # Define the schema for structured output
        outline_schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "slides": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "key_points": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["title", "key_points"]
                    }
                }
            },
            "required": ["title", "slides"]
        }

        system_prompt = """
        You are an expert presentation designer who creates clear, engaging, and well-structured
        presentation outlines. Your outlines should be comprehensive yet concise, covering all
        important information in a logical flow.
        """

        prompt = f"""
        Based on the following processed material, create a detailed outline for a presentation.
        The outline should include a compelling title and a series of slides with clear titles
        and key points to cover in each slide.

        PROCESSED MATERIAL:
        {processed_material}

        Create an outline that:
        1. Has a clear and engaging title
        2. Includes an introduction slide
        3. Presents information in a logical sequence
        4. Covers all key points from the material
        5. Includes a conclusion/summary slide

        For each slide, provide:
        - A clear, concise title
        - 3-5 key points to cover in bullet form
        """

        return {
            "processed_material": processed_material,
            "outline_schema": outline_schema,
            "system_prompt": system_prompt,
            "prompt": prompt
        }

    def exec(self, prep_res):
        """
        Execute the LLM call to generate the outline.

        Args:
            prep_res: Result from prep step

        Returns:
            Generated outline from LLM
        """
        if "error" in prep_res:
            return {"error": prep_res["error"]}

        # Generate the outline using structured output
        outline = self.llm_wrapper.generate_structured(
            prompt=prep_res["prompt"],
            output_schema=prep_res["outline_schema"],
            system_prompt=prep_res["system_prompt"],
            temperature=0.4
        )

        return outline

    def post(self, shared, prep_res, exec_res):
        """
        Update the shared state with the generated outline.

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

        # Update the shared state with the outline
        shared["outline"] = exec_res

        # Return default action
        return "default"
