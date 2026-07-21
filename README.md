# Loomcast

Python SDK and CLI for seamlessly managing local LLM runtimes (**Ollama** and **LM Studio**).

## Installation

```bash
pip install -e .
```

## Quick Start

### CLI

```bash
loomcast status
loomcast list
loomcast chat ollama llama3 "Hello world!"
```

### Python SDK

```python
import loomcast

manager = loomcast.LoomcastManager()
response = manager.chat("llama3", [{"role": "user", "content": "Hello!"}])
print(response)
```
