# assets-extractor

A small, offline tool that pulls pentest mission assets out of the documents you get at kickoff: scope sheets, rules of engagement, emails, spreadsheets, screenshots. It finds IP addresses, CIDR ranges and domain names with regexes, and uses a local LLM to extract test accounts (usernames, domains, passwords, hashes).

Everything runs locally. The tool installs a Python audit hook that blocks all outgoing network connections at startup, so client documents never leave your machine.

## Features

- **Many input formats** via [MarkItDown](https://github.com/microsoft/markitdown): PDF, DOCX, PPTX, XLSX, XLS, Outlook `.msg`, TXT, Markdown and more.
- **Images** (`.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff`, `.tif`, `.webp`, `.gif`): transcribed and parsed with a local vision-language model, or with Tesseract OCR in `--no-llm` mode.
- **Regex extraction** of IPv4 addresses, IPv4 CIDR ranges and domain names. Regexes are configurable.
- **LLM extraction** of accounts using [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) with grammar-constrained JSON output, so results always match the expected schema. Extracted usernames that don't literally appear in the source text are dropped.
- **No network access** while running.

## Requirements

- Python 3.11 or later (3.13 recommended)
- [uv](https://docs.astral.sh/uv/) (optional, [mise](https://mise.jdx.dev/) is supported too)
- A C/C++ toolchain, since `llama-cpp-python` builds llama.cpp on install
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed on the system, for image extraction in `--no-llm` mode
- GGUF model files, for LLM mode (see below)

## Installation

With uv:

```bash
git clone https://github.com/lap1nou/assets-extractor.git
cd assets-extractor
uv sync
```

With mise, entering the directory installs the toolchain (Python, uv, ruff) and syncs dependencies automatically through the `enter` hook:

```bash
git clone https://github.com/lap1nou/assets-extractor.git
cd assets-extractor
mise trust
```

With pip:

```bash
pip install .
```

### Models

LLM mode uses Qwen3-VL-4B-Instruct in GGUF format. Two files are needed:

| File | Purpose |
|------|---------|
| `Qwen3VL-4B-Instruct-Q4_K_M.gguf` | Language model, used for text and images |
| `mmproj-Qwen3VL-4B-Instruct-Q8_0.gguf` | Vision projector, used for images only |

Download them from Hugging Face and either place them in the directory you run the tool from, or set absolute paths in the config file (see [Configuration](#configuration)). Other GGUF models can be used by changing the config, as long as they are compatible with llama.cpp.

## Usage

```bash
uv run assets-extractor -f <file> [--no-llm]
```

| Option | Description |
|--------|-------------|
| `-f`, `--file` | Path of the file to extract assets from (required) |
| `--no-llm` | Skip the LLM. Faster and needs no model, but accounts are not extracted |

### Examples

Extract everything from a scope document:

```bash
uv run assets-extractor -f scope.pdf
```

Regex-only extraction from a spreadsheet:

```bash
uv run assets-extractor -f targets.xlsx --no-llm
```

Extract hosts and ranges from a screenshot with the vision model:

```bash
uv run assets-extractor -f network-diagram.png
```

## How it works

**Documents** are converted to Markdown with MarkItDown. The text then goes through the regexes, and, unless `--no-llm` is set, through the LLM for account extraction.

**Images** are sent to the vision model, which first transcribes all visible text and then extracts hosts and accounts from that transcript. With `--no-llm`, Tesseract does the OCR and the regexes run on its output instead.

## Output

Results are printed to stdout in three blocks.

Hosts found by the regexes, one entry per IP or domain:

```json
[
  {"ip": "10.20.0.15", "hostname": "", "role": ""},
  {"ip": "", "hostname": "vpn.corp.local", "role": ""}
]
```

IP ranges:

```json
[
  {"range": "10.20.0.0/24", "name": ""}
]
```

Accounts found by the LLM:

```json
{
  "accounts": [
    {
      "username": "svc_audit",
      "domain": "ACME",
      "host": "10.20.0.15",
      "password": "Summer2024!",
      "hash": null
    }
  ]
}
```

For images in LLM mode, the output is a list of hosts with `ip` and `hostname` fields.

## Configuration

On first run, a default config is copied to `~/.assets_extractor/config.toml`. Edit that file to change models, prompts or regexes.

```toml
[regexes]
ipv4 = '...'
domain = '...'
ipv4_cidr = '...'

[llm]
# prompt = """..."""      # system prompt for text extraction
# prompt_vl = """..."""   # prompt for image extraction
model = "Qwen3VL-4B-Instruct-Q4_K_M.gguf"
model_vl = "mmproj-Qwen3VL-4B-Instruct-Q8_0.gguf"
```

Relative model paths are resolved from the current working directory, so absolute paths are the safer choice.

## Development

```bash
mise run lint   # ruff format + ruff check
mise run test   # pytest with coverage
```

Or directly:

```bash
uv run ruff format . && uv run ruff check .
uv run pytest
```

## Disclaimer

This tool is meant for authorized security assessments. The documents it processes often contain sensitive client data and credentials, so handle its output accordingly.
