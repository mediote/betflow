import json
import os
from typing import Any, Dict, List

import openai
from dotenv import load_dotenv
from fastapi import HTTPException
from promptflow.core import tool

load_dotenv()


@tool
def process_clauses(
    document_text: str, prompts: Dict[str, str]
) -> Dict[str, Any]:
    """
    Processes each prompt using the Azure OpenAI LLM and collects the responses as JSON objects.

    Args:
        document_text (str): The text extracted from the document.
        prompts (Dict[str, str]): A dictionary where keys are prompt names
                                  and values are the prompt instructions.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with prompt names as keys
                              and JSON responses as values.
    """

    if not document_text.strip():
        raise HTTPException(
            status_code=400,
            detail="The 'document_text' cannot be empty or only whitespace.",
        )

    if not prompts:
        raise HTTPException(
            status_code=400, detail="The 'prompts' dictionary cannot be empty."
        )

    clausule_categories = {}

    openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
    openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
    openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    model_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    if not all([openai.api_key, openai.api_base, openai.api_version, model_name]):
        raise HTTPException(
            status_code=500,
            detail="Azure OpenAI configuration is incomplete. Please check your environment variables.",
        )

    for prompt_name, prompt_instructions in prompts.items():
        messages = [
            {"role": "system", "content": prompt_instructions},
            {"role": "user", "content": document_text},
        ]

        try:
            response = openai.chat.completions.create(
                model=model_name,
                messages=messages,
                #temperature=0,
                response_format={"type": "text"},
            )

            response_text = response.choices[0].message.content

            try:
                parsed_json = json.loads(response_text)
            except json.JSONDecodeError:
                parsed_json = {
                    "error": "Invalid JSON format returned by the model.",
                    "response": response_text,
                }

            clausule_categories[prompt_name] = parsed_json
            # clausule_categories.extend(parsed_json)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing prompt '{prompt_name}': {str(e)}",
            )

    return clausule_categories
