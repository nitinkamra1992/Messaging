import os
from openai import OpenAI


class LLM:
    """OpenAI GPT model"""

    def __init__(self):
        """Initialize the LLM"""
        # Check OpenAI API Key
        if "OPENAI_API_KEY" not in os.environ:
            raise Exception(
                "Please export your OpenAI API key in the OPENAI_API_KEY variable before running the program."
            )
        self.client = OpenAI()

    async def query(self, instruction, sys_prompt="", **kwargs):
        """Query the LLM with a system prompt and user instructions"""
        # Prompt the LLM
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": instruction}
            ]
        ).choices[0].message.content

        return response