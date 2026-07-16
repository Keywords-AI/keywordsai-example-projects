from __future__ import annotations

from aleph_alpha_client import (
    BatchSemanticEmbeddingRequest,
    EmbeddingRequest,
    EmbeddingV2Request,
    Prompt,
    SemanticEmbeddingRequest,
    SemanticRepresentation,
)
from aleph_alpha_client.embedding import InstructableEmbeddingRequest
from _shared import (
    example_attributes,
    make_custom_identifier,
    make_respan,
    model_name,
    print_result,
    sync_client_context,
    workflow,
    workflow_name,
)

EXAMPLE_NAME = "embeddings"


@workflow(name=workflow_name(EXAMPLE_NAME))
def _embeddings_workflow(client) -> str:
    classic = client.embed(
        request=EmbeddingRequest(
            prompt=Prompt.from_text("Trace a classic Aleph Alpha embedding."),
            layers=[-1],
            pooling=["mean"],
        ),
        model=model_name(),
    )
    openai_style = client.embeddings(
        request=EmbeddingV2Request(
            input=["first embedding input", "second embedding input"],
            dimensions=3,
        ),
        model=model_name(),
    )
    semantic = client.semantic_embed(
        request=SemanticEmbeddingRequest(
            prompt=Prompt.from_text("semantic search query"),
            representation=SemanticRepresentation.Query,
        ),
        model=model_name(),
    )
    batch = client.batch_semantic_embed(
        request=BatchSemanticEmbeddingRequest(
            prompts=[Prompt.from_text("document one"), Prompt.from_text("document two")],
            representation=SemanticRepresentation.Document,
        ),
        model=model_name(),
    )
    instructable = client.instructable_embed(
        request=InstructableEmbeddingRequest(
            input=Prompt.from_text("hello there"),
            instruction="Represent this text as a greeting.",
        ),
        model=model_name(),
    )
    return (
        f"classic={classic.num_tokens_prompt_total}; "
        f"openai_style={len(openai_style.data)}; "
        f"semantic={len(semantic.embedding)}; "
        f"batch={len(batch.embeddings)}; "
        f"instructable={len(instructable.embedding)}"
    )


def run_embeddings() -> None:
    respan = make_respan(EXAMPLE_NAME)
    custom_identifier = make_custom_identifier(EXAMPLE_NAME)
    text = ""
    mode = "unknown"
    try:
        with sync_client_context() as (client, mode):
            with example_attributes(EXAMPLE_NAME, custom_identifier):
                print(f"custom_identifier={custom_identifier}", flush=True)
                print(f"workflow_name={workflow_name(EXAMPLE_NAME)}", flush=True)
                text = _embeddings_workflow(client)
    finally:
        respan.flush()
        respan.shutdown()

    print_result(EXAMPLE_NAME, custom_identifier, mode, text)


if __name__ == "__main__":
    run_embeddings()
