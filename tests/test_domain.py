from loomcast.domain.entities import CatalogEntry, ChatMessage, Model, RuntimeType


def test_runtime_type_enum():
    assert RuntimeType.OLLAMA == "ollama"
    assert RuntimeType.LMSTUDIO == "lmstudio"
    assert RuntimeType("ollama") == RuntimeType.OLLAMA
    assert RuntimeType("lmstudio") == RuntimeType.LMSTUDIO


def test_model_entity_creation():
    model = Model(
        name="llama3:latest",
        runtime_type=RuntimeType.OLLAMA,
        size_bytes=4700000000,
        digest="sha256:1234567890abcdef",
        details={"family": "llama", "parameter_size": "8B"},
    )
    assert model.name == "llama3:latest"
    assert model.runtime_type == RuntimeType.OLLAMA
    assert model.size_bytes == 4700000000
    assert model.digest == "sha256:1234567890abcdef"
    assert model.details["family"] == "llama"


def test_catalog_entry_creation():
    entry = CatalogEntry(
        name="mistral:7b",
        description="Mistral 7B model",
        publisher="Mistral AI",
        tags=["7b", "general"],
        default_runtime=RuntimeType.OLLAMA,
    )
    assert entry.name == "mistral:7b"
    assert entry.publisher == "Mistral AI"
    assert "7b" in entry.tags
    assert entry.default_runtime == RuntimeType.OLLAMA


def test_chat_message_creation():
    msg = ChatMessage(role="user", content="Hello Loomcast!")
    assert msg.role == "user"
    assert msg.content == "Hello Loomcast!"
