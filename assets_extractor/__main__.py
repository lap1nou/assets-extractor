import argparse
import sys
from markitdown import MarkItDown
from assets_extractor.utils.utils import domains_ips_to_json, ips_cidr_to_json
from assets_extractor.regexes.regexes import extract_assets
from assets_extractor.llm.llm import llm_extract
from assets_extractor.llm.vl import vl_extract
from assets_extractor.config.config import AppConfig
from pathlib import Path
from rich.console import Console

import json

def _block_network(event, args):
    if event in {"socket.connect", "socket.getaddrinfo", "socket.gethostbyname"}:
        raise RuntimeError(f"Network access blocked: {event} {args}")


def main():
    # Forbid network using a hook
    sys.addaudithook(_block_network)

    parser = argparse.ArgumentParser(
        prog="assets_extractor",
        description="""
            Assets-extractor: A tool to extract redentials and assets
            from various sources (TXT, PDF, XLSX, ...).
        """,
    )
    parser.add_argument('-f', '--file', required=True, help="The file path you want to extract assets from.")
    parser.add_argument('--no-llm', action="store_true", required=False, help="Do not use an LLM, but will not extract credentials.")
    args = parser.parse_args()

    console = Console()
    config = AppConfig()

    IMAGE_EXT = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp", ".gif"}
    if Path(args.file).suffix.lower() in IMAGE_EXT:
        if not args.no_llm:
            with console.status("Running VLM..."):
                result = vl_extract(config.llm, args.file)

            console.print_json(print(json.dumps([a.model_dump() for a in result.assets], indent=2, ensure_ascii=False)))
        else:
            with console.status("Running Pytesseract..."):
                result_text = pytesseract.image_to_string(Image.open(args.file))
                ips, ips_cidr, domains = extract_assets(config.regexes, result_text)

                print(domains_ips_to_json(ips, domains))
                print(ips_cidr_to_json(ips_cidr))
    else:
        md = MarkItDown()
        result = md.convert(args.file)
        result_text = result.markdown

        ips, ips_cidr, domains = extract_assets(config.regexes, result_text)

        print(domains_ips_to_json(ips, domains))
        print(ips_cidr_to_json(ips_cidr))

        if not args.no_llm:
            assets = llm_extract(result_text, config_llm=config.llm)
            print(assets.model_dump_json(indent=2))