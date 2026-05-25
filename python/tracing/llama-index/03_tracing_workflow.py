"""Embedding: call the LlamaIndex OpenAI embedding integration."""

from _shared import build_embedding_model, create_respan, print_result, traced_example


def run_embedding() -> None:
    context = create_respan(
        app_name="llama-index-03-embedding",
        example_name="03_embedding",
    )
    embed_model = build_embedding_model(settings=context.settings)

    with traced_example(context):
        embedding = embed_model.get_text_embedding(
            "LlamaIndex uses embeddings to retrieve relevant document chunks."
        )

    print_result("Embedding dimensions", len(embedding))
    print_result("Example run id", context.run_id)
    context.respan.flush()


if __name__ == "__main__":
    run_embedding()
