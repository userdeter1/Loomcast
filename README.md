# Loomcast

Python SDK and CLI for seamlessly managing local LLM runtimes (**Ollama** and **LM Studio**).

## Installation

```bash
pip install -e .
```

## Quick Start

### CLI Usage

```bash
# Check status of local runtimes
loomcast status

# List installed models
loomcast list

# Search catalog for models
loomcast search code

# Recommend models for a specific task or tag
loomcast recommend coding

# Batch install all models in a category
loomcast install-category code --backend ollama

# Send a prompt to a model
loomcast chat llama3 "Hello world!" --backend ollama

# Verify installed model integrity
loomcast verify llama3 --backend ollama
```

### Python SDK Usage

```python
import loomcast

# Initialize manager
manager = loomcast.LoomcastManager()

# Search catalog
results = loomcast.search("code")
for model in results:
    print(model.name, model.description)

# Recommend models for a task
recs = loomcast.recommend("coding")

# Batch install category
installed, failed = loomcast.install_category("code", runtime_type="ollama")

# Send chat messages
response = loomcast.chat("llama3", [{"role": "user", "content": "Hello!"}], runtime_type="ollama")
print(response)

# Verify model integrity
verification = loomcast.verify("llama3", runtime_type="ollama")
print(f"Verified: {verification.verified}, Digest: {verification.digest}")
```
