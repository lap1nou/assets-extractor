import json

from typing import Literal
from llama_cpp import Llama
from assets_extractor.config.config import ConfigLLM
from assets_extractor.llm.models import MissionAssets, Account, SCHEMA

def llm_extract(chunk: str, config_llm: ConfigLLM = ConfigLLM()) -> MissionAssets:
    llm = Llama(
    model_path=config_llm.model,
    n_ctx=4096,
    verbose=False,
    )
    response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": config_llm.prompt},
            {"role": "user", "content": chunk},
        ],
        # The constraint: the sampler can only emit tokens that keep the
        # output valid against SCHEMA (converted to a grammar internally).
        response_format={"type": "json_object", "schema": SCHEMA},
        temperature=0,
        max_tokens=1024,
    )
    choice = response["choices"][0]
 
    # If the model ran out of tokens, the JSON is cut off: use smaller chunks.
    if choice["finish_reason"] == "length":
        raise ValueError("Output truncated: reduce chunk size or raise max_tokens")
 
    # Parse + validate into Python objects.
    result = MissionAssets.model_validate_json(choice["message"]["content"])

    # Drop anything that doesn't actually appear in the source text.
    result.accounts = [a for a in result.accounts if a.username in chunk]

    return result
