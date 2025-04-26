import os
from typing import Dict, List

from promptflow.core import tool


@tool
def load_prompts(prompt_base_dir: str, prompt_list: List[str]) -> Dict[str, str]:
    """
    Loads specific prompt from the specified base directory.

    Args:
        prompt_list (List[str]): A list of prompt names (without extension) to load.

    Returns:
        Dict[str, str]: A dictionary where keys are prompt names and
        values are the content of the prompt files.
    """

    base_dir = prompt_base_dir

    if not os.path.isdir(base_dir):
        raise ValueError(f"The provided base directory does not exist: {base_dir}")

    prompts = {}

    for root, _, files in os.walk(base_dir):
        for file_name in files:
            if file_name.endswith(".txt"):
                prompt_name = file_name.replace(".txt", "")

                if prompt_name not in prompt_list:
                    continue

                file_path = os.path.join(root, file_name)
                with open(file_path, "r", encoding="utf-8") as file:
                    prompts[prompt_name] = file.read().strip()

    if not prompts:
        raise ValueError(
            "No valid prompt files were found in the specified base directory."
        )

    return prompts
