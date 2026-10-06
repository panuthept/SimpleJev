"""vLLM backend.

One forward pass per (state, question). Logits are read at the last position and
only the first token of each label is compared, then softmaxed across labels so
nothing outside the option set can win.

Phase 1 will add: shared-state prefill with KV-cache reuse across questions, and
multi-token label scoring (sum of log-probs) for labels that are not single tokens.
"""

from __future__ import annotations

from openjev.backends.base import Backend


class VLLMBackend(Backend):
    def __init__(self, model_id: str = "Qwen/Qwen2.5-0.5B-Instruct", api_key: str | None = None, base_url: str | None = None, **kwargs):
        self.model_id = model_id
        self.name = f"openjev-vllm/{model_id}"
        self.api_key = api_key
        self.base_url = base_url
        self._client = None
        self._tok = None

    def load(self) -> None:
        if self._client is not None:
            return
        try:
            from openai import OpenAI
            from transformers import AutoTokenizer
        except ImportError as e:  # pragma: no cover
            raise ImportError("Install with: pip install 'openjev[vllm]'") from e
        self._tok = AutoTokenizer.from_pretrained(self.model_id)
        self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def _first_token_id(self, label: str) -> int:
        ids = self._tok.encode(label, add_special_tokens=False)
        return ids[0]

    def score_options(self, prompt: str, labels: list[str]) -> tuple[list[float], int]:
        self.load()

        response = self._client.chat.completions.create(
            model=self.model_id,
            messages=[{"role": "user", "content": prompt}],
            logprobs=True,
            top_logprobs=20,
        )
        print(response.choices[0].message.content)
        for token in response.choices[0].logprobs.content:
            print(
                token.token,
                token.logprob,
                token.top_logprobs
            )

        # last = out.logits[0, -1].float()
        # ids = [self._first_token_id(label) for label in labels]
        # logits = [float(last[i]) for i in ids]
        # return logits, int(enc["input_ids"].shape[1])
