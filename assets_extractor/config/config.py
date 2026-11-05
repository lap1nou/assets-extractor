import json
import shutil
import tomllib
from assets_extractor.llm.models import SCHEMA
from pathlib import Path


class AppConfig:
    ASSETS_EXTRACTOR_HOME_FOLDER_NAME = Path.home() / ".assets_extractor"
    CONFIG_FILENAME = "config.toml"

    def __init__(
        self, config_path: str = ASSETS_EXTRACTOR_HOME_FOLDER_NAME / CONFIG_FILENAME
    ):
        if not Path(config_path).is_file():
            Path(config_path).parent.mkdir(exist_ok=True)

            default_config_path = Path(__file__).parent / AppConfig.CONFIG_FILENAME
            shutil.copy(default_config_path, config_path)

        with open(config_path, "rb") as config_file:
            config_data = tomllib.load(config_file)

        self.regexes = ConfigRegexes(**config_data["regexes"])
        self.llm = ConfigLLM(**config_data["llm"])


class ConfigRegexes:
    def __init__(
        self,
        ipv4: str = r"(?<![\d.])(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?![\d/]|\.\d)",
        ipv4_cidr: str = r"(?<![\w@.-])(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+(?:[A-Za-z]{2,63}|xn--[A-Za-z0-9-]{1,59})(?![\w-])",
        domain: str = r"(?<![\d.])(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)/(?:3[0-2]|[12]?\d)(?!\d)",
    ):
        self.ipv4 = ipv4
        self.ipv4_cidr = ipv4_cidr
        self.domain = domain


class ConfigLLM:
    def __init__(
        self,
        prompt: str = f"""
            You extract pentest mission assets from text.
            Only report values that literally appear in the text; never invent any.
            If nothing matches a category, return an empty list.\n
            Output JSON matching this schema:\n{json.dumps(SCHEMA)}
            """,
        prompt_vl: str = f"""
            First copy all visible text verbatim into 'transcript', then extract the hosts (IP + hostname if present) or ip range from it.
            """,
        model: str = "Qwen3VL-4B-Instruct-Q4_K_M.gguf",
        model_vl: str = "mmproj-Qwen3VL-4B-Instruct-Q8_0.gguf",
        ):
        self.prompt = prompt
        self.prompt_vl = prompt_vl
        self.model = model
        self.model_vl = model_vl
