from llama_cpp.llama_chat_format import Qwen25VLChatHandler
from llama_cpp import Llama
import mimetypes
import base64
import json
from pathlib import Path
from assets_extractor.llm.models import ImageAssets, Host
from assets_extractor.config.config import ConfigLLM
from assets_extractor.llm.prompt import build_image_messages

def vl_extract(config_llm: ConfigLLM = ConfigLLM(), path: str = ""):
    path = Path(path)
    llm = Llama(model_path=config_llm.model,
        chat_handler=Qwen25VLChatHandler(clip_model_path=config_llm.model_vl, verbose=False,),
        n_ctx=8192, verbose=False)
    mime = mimetypes.guess_type(path.name)[0] or "image/png"

    out = llm.create_chat_completion(
        messages=build_image_messages(path.read_bytes(), mime),
        response_format={"type": "json_object", "schema": ImageAssets.model_json_schema()},
        temperature=0)

    r = ImageAssets.model_validate_json(out["choices"][0]["message"]["content"])
    #r.assets = [a for a in r.assets if a.value in r.transcript]          # same anti-hallucination filter
    #r.accounts = [a for a in r.accounts if a.username in r.transcript]

    return r