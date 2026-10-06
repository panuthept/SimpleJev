"""Backend registry."""

from __future__ import annotations

from openjev.backends.base import Backend


def get_backend(name: str = "mock", **kwargs) -> Backend:
    if name == "mock":
        from openjev.backends.mock import MockBackend

        return MockBackend()
    if name == "hf":
        from openjev.backends.hf import HFBackend

        return HFBackend(**kwargs)
    if name == "vllm":
        from openjev.backends.vllm import VLLMBackend

        return VLLMBackend(**kwargs)
    raise ValueError(f"Unknown backend '{name}'. Available: mock, hf, vllm (mlx, typesafe coming in Phase 3)")


__all__ = ["Backend", "get_backend"]
