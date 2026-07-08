from respan import Respan, workflow

from _shared import (
    DeterministicEmbeddingFunction,
    collection_name,
    create_chroma_client,
    create_respan,
    finish_respan,
    print_result,
    sample_records,
    workflow_attributes,
)

WORKFLOW_NAME = "chroma_query_and_filters_workflow"


@workflow(name=WORKFLOW_NAME)
def run_query_and_filters() -> dict:
    client = create_chroma_client()
    collection = client.create_collection(
        collection_name(WORKFLOW_NAME),
        embedding_function=DeterministicEmbeddingFunction(),
        metadata={"purpose": "query-filters"},
    )
    records = sample_records()

    collection.add(
        ids=records["ids"],
        documents=records["documents"],
        metadatas=records["metadatas"],
    )

    text_query = collection.query(
        query_texts=["Which documents are about programming languages?"],
        n_results=2,
        where={"topic": "programming"},
        include=["documents", "metadatas", "distances"],
    )
    document_filter_query = collection.query(
        query_texts=["What should be salted?"],
        n_results=1,
        where_document={"$contains": "salted"},
        include=["documents", "metadatas", "distances"],
    )

    return {
        "text_query": text_query,
        "document_filter_query": document_filter_query,
    }


def main() -> None:
    respan = create_respan(WORKFLOW_NAME)
    try:
        with Respan.propagate_attributes(**workflow_attributes(WORKFLOW_NAME)):
            result = run_query_and_filters()
        print_result(WORKFLOW_NAME, result)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    main()
