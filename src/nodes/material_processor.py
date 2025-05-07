"""
Material Processor Node for processing input material.
"""
from typing import Dict, Any, List, Optional
from pocketflow import Node

class MaterialProcessor(Node):
    """
    Node for processing input material and extracting key information.
    """

    def __init__(self, llm_wrapper, max_retries=1):
        """
        Initialize the material processor node.

        Args:
            llm_wrapper: LLM wrapper for making API calls
            max_retries: Maximum number of retries for LLM calls
        """
        super().__init__(max_retries=max_retries)
        self.llm_wrapper = llm_wrapper

    def prep(self, shared):
        """
        Prepare the input material for processing.

        Args:
            shared: Shared state dictionary

        Returns:
            Dictionary with material and prompts
        """
        material = shared.get("material", "")
        if not material:
            return {"error": "No material provided"}

        system_prompt = """
        You are an expert at analyzing and extracting key information from text.
        Your task is to process the provided material and identify the most important
        concepts, facts, and ideas that should be included in a presentation.
        """

        prompt = f"""
        Please analyze the following material and extract the key information that should be
        included in a presentation. Focus on the main ideas, important facts, and concepts.

        MATERIAL:
        {material}

        Please provide a structured analysis with the following:
        1. Main topic and purpose
        2. Key concepts and ideas
        3. Important facts and data
        4. Potential audience for this material
        5. Suggested tone and style for the presentation
        """

        print(material)

        return {
            "material": material,
            "system_prompt": system_prompt,
            "prompt": prompt
        }

    def exec(self, prep_res):
        """
        Execute the LLM call to process the material.

        Args:
            prep_res: Result from prep step

        Returns:
            Processed material from LLM
        """
        if "error" in prep_res:
            return prep_res["error"]

        processed_material = self.llm_wrapper.generate(
            prompt=prep_res["prompt"],
            system_prompt=prep_res["system_prompt"],
            temperature=0.3,
            max_tokens=2000
        )

        return processed_material

    def post(self, shared, prep_res, exec_res):
        """
        Update the shared state with processed material.

        Args:
            shared: Shared state dictionary
            prep_res: Result from prep step
            exec_res: Result from exec step

        Returns:
            Action string for flow control
        """
        if isinstance(exec_res, str) and exec_res.startswith("Error:"):
            shared["error"] = exec_res
            return "error"

        # Update the shared state with processed material
        shared["processed_material"] = exec_res

        # Return default action
        return "default"
