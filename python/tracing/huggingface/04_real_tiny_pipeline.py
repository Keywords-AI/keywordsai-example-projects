"""Trace an actual local Transformers pipeline without downloading a model."""

from __future__ import annotations

import torch
from respan import workflow
from tokenizers import Tokenizer
from tokenizers.models import WordLevel
from tokenizers.pre_tokenizers import Whitespace
from transformers import (
    GPT2Config,
    GPT2LMHeadModel,
    PreTrainedTokenizerFast,
    TextGenerationPipeline,
)

from _shared import build_respan, print_result

EXAMPLE_NAME = "real-tiny-pipeline"
WORKFLOW_NAME = "huggingface_04_real_tiny_pipeline"


def build_pipeline() -> TextGenerationPipeline:
    vocabulary = {
        "[PAD]": 0,
        "[UNK]": 1,
        "[EOS]": 2,
        "Tracing": 3,
        "Hugging": 4,
        "Face": 5,
        "locally": 6,
        "keeps": 7,
        "telemetry": 8,
        "repeatable": 9,
        ".": 10,
    }
    tokenizer_backend = Tokenizer(
        WordLevel(vocab=vocabulary, unk_token="[UNK]")
    )
    tokenizer_backend.pre_tokenizer = Whitespace()
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer_backend,
        unk_token="[UNK]",
        pad_token="[PAD]",
        eos_token="[EOS]",
    )

    torch.manual_seed(17)
    model = GPT2LMHeadModel(
        GPT2Config(
            vocab_size=len(vocabulary),
            name_or_path="respan-local-tiny-gpt2",
            n_positions=32,
            n_ctx=32,
            n_embd=16,
            n_layer=1,
            n_head=1,
            bos_token_id=2,
            eos_token_id=2,
            pad_token_id=0,
        )
    )
    model.eval()
    return TextGenerationPipeline(model=model, tokenizer=tokenizer, device=-1)


@workflow(name=WORKFLOW_NAME)
def execute_real_tiny_generation() -> list[dict[str, str]]:
    return build_pipeline()(
        "Tracing Hugging Face locally",
        max_new_tokens=4,
        do_sample=False,
    )


def run() -> list[dict[str, str]]:
    respan = build_respan(example_name=EXAMPLE_NAME, workflow_name=WORKFLOW_NAME)
    try:
        result = execute_real_tiny_generation()
        print_result("real_tiny_generation", result)
        return result
    finally:
        respan.shutdown()


if __name__ == "__main__":
    run()
