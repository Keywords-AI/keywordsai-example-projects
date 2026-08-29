from _shared import (
    create_respan,
    finish_respan,
    marqo_client,
    print_result,
    unique_index_name,
    workflow_attributes,
)
from respan import Respan, workflow

WORKFLOW_NAME = "marqo_document_search_workflow"


@workflow(name=WORKFLOW_NAME)
def run_quickstart() -> dict:
    index_name = unique_index_name()
    documents = [
        {
            "_id": "lancedb",
            "title": "LanceDB",
            "description": "An embedded vector database for multimodal AI.",
        },
        {
            "_id": "marqo",
            "title": "Marqo",
            "description": "A search engine with tensor search and inference.",
        },
        {
            "_id": "respan",
            "title": "Respan",
            "description": "Observability for AI application traces and logs.",
        },
    ]

    with marqo_client() as client:
        client.create_index(index_name)
        index = client.index(index_name)
        try:
            index.add_documents(
                documents,
                tensor_fields=["title", "description"],
            )
            response = index.search(q="AI observability", limit=2)
            hits = [
                {
                    "id": hit.get("_id"),
                    "title": hit.get("title"),
                    "score": hit.get("_score"),
                }
                for hit in response.get("hits", [])
            ]
            return {
                "index_name": index_name,
                "indexed": len(documents),
                "hits": hits,
            }
        finally:
            index.delete()


def main() -> None:
    respan = create_respan(WORKFLOW_NAME)
    try:
        with Respan.propagate_attributes(**workflow_attributes(WORKFLOW_NAME)):
            result = run_quickstart()
        print_result(WORKFLOW_NAME, result)
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    main()
