"""vLLM backend.

One forward pass per (state, question). Logits are read at the last position and
only the first token of each label is compared, then softmaxed across labels so
nothing outside the option set can win.

Phase 1 will add: shared-state prefill with KV-cache reuse across questions, and
multi-token label scoring (sum of log-probs) for labels that are not single tokens.
"""

from __future__ import annotations

from openai import OpenAI
from transformers import AutoTokenizer
from openjev.backends.base import Backend


class VLLMBackend(Backend):
    def __init__(self, api_key: str | None = None, base_url: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.base_url = base_url
        self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self._toks = {}
        self.load()

    def load(self) -> None:
        # Pre-load tokenizers for all models that in client
        for model in self._client.models.list().data:
            self.init_tokenizer(model.id)

    def init_tokenizer(self, model: str) -> None:
        if model not in self._toks:
            self._toks[model] = AutoTokenizer.from_pretrained(model)

    def _first_token(self, model: str, label: str) -> int:
        if model not in self._toks:
            self.init_tokenizer(model)

        ids = self._toks[model].encode(label, add_special_tokens=False)
        return self._toks[model].decode(ids[0])

    def score_options(self, model: str, prompt: str, labels: list[str]) -> tuple[list[float], int]:
        if model not in self._toks:
            self.init_tokenizer(model)
        enc = self._toks[model](prompt, return_tensors="pt")

        response = self._client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            logprobs=True,
            top_logprobs=20,
            extra_body={
                "chat_template_kwargs": {
                    "enable_thinking": False
                }
            }
        )
        pred_tokens = {top_logprob.token: top_logprob.logprob for top_logprob in response.choices[0].logprobs.content[0].top_logprobs}
        cand_tokens = [self._first_token(model, label) for label in labels]
        logits = [pred_tokens.get(token, float("-inf")) for token in cand_tokens]
        return logits, int(enc["input_ids"].shape[1])
