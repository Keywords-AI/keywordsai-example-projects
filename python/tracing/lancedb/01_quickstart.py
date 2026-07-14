from tempfile import TemporaryDirectory

from respan import Respan, workflow

from _shared import create_respan, finish_respan, print_result, workflow_attributes

WORKFLOW_NAME = "lancedb_local_vector_search_workflow"


@workflow(name=WORKFLOW_NAME)
def run_quickstart() -> dict:
    import lancedb

    with TemporaryDirectory(prefix="respan-lancedb-") as database_dir:
        db = lancedb.connect(database_dir)
        table = db.create_table(
            "documents",
            data=[
                {
                    "id": "python",
                    "text": "Python is a general-purpose programming language.",
                    "topic": "programming",
                    "vector": [0.9, 0.1, 0.0, 0.0],
                }
            ],
        )
        table.add(
            [
                {
                    "id": "rust",
                    "text": "Rust emphasizes memory safety and performance.",
                    "topic": "programming",
                    "vector": [0.8, 0.2, 0.0, 0.0],
                },
                {
                    "id": "pasta",
                    "text": "Pasta water should be salted before cooking.",
                    "topic": "cooking",
                    "vector": [0.1, 0.9, 0.0, 0.0],
                },
            ]
        )

        matches = (
            table.search([0.95, 0.05, 0.0, 0.0])
            .select(["id", "text", "topic"])
            .limit(2)
            .to_list()
        )
        table_names = db.table_names()
        db.drop_table("documents")

    return {"table_names": table_names, "matches": matches}


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
