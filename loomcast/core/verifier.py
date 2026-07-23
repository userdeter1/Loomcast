from __future__ import annotations

from loomcast.common.exceptions import ModelNotFoundError
from loomcast.domain.entities import RuntimeType, VerificationResult
from loomcast.ports.runtime import RuntimePort


class ModelVerifier:
    """Service for verifying installed model integrity across local runtimes."""

    def __init__(self, runtimes: dict[RuntimeType, RuntimePort]):
        self.runtimes = runtimes

    def verify(self, model: str, runtime_type: RuntimeType) -> VerificationResult:
        """
        Verify integrity of an installed model for the specified runtime backend.

        Raises:
            ModelNotFoundError: If the model is not installed in the specified runtime.
        """
        adapter = self.runtimes.get(runtime_type)
        if adapter is None or not adapter.is_model_installed(model):
            raise ModelNotFoundError(model_name=model, runtime_name=runtime_type.value)

        if runtime_type == RuntimeType.OLLAMA:
            digest: str | None = None
            if hasattr(adapter, "get_model_digest"):
                digest = adapter.get_model_digest(model)

            if digest and digest.strip():
                return VerificationResult(
                    model=model,
                    runtime_type=runtime_type,
                    verified=True,
                    digest=digest,
                    message="Ollama model integrity verified via server digest.",
                )
            else:
                return VerificationResult(
                    model=model,
                    runtime_type=runtime_type,
                    verified=False,
                    digest=None,
                    message="Ollama model digest is missing or empty.",
                )

        elif runtime_type == RuntimeType.LMSTUDIO:
            # LM Studio operates using an OpenAI-compatible API (/v1/models) which exposes
            # model identifiers but does not expose cryptographic digests or hashes.
            # Therefore, automated integrity verification via API is unavailable for LM Studio.
            return VerificationResult(
                model=model,
                runtime_type=runtime_type,
                verified=False,
                digest=None,
                message=(
                    "LM Studio n'expose pas de digest vérifiable via son API ; "
                    "vérification non disponible pour ce runtime."
                ),
            )

        return VerificationResult(
            model=model,
            runtime_type=runtime_type,
            verified=False,
            digest=None,
            message=f"Verification not supported for runtime type '{runtime_type}'.",
        )
