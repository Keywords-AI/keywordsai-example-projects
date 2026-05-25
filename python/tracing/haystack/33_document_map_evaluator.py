"""One-script example for DocumentMAPEvaluator."""

from _shared import configure_respan, finish_respan, print_result


def run_document_map_evaluator_example():
    respan = configure_respan("haystack-document-map-evaluator")
    try:
        from haystack import Document
        from haystack.components.evaluators import DocumentMAPEvaluator

        relevant = [Document(content="A"), Document(content="B")]
        retrieved = [relevant[0], Document(content="C"), relevant[1]]
        result = DocumentMAPEvaluator().run(
            ground_truth_documents=[relevant],
            retrieved_documents=[retrieved],
        )
        print_result("DocumentMAPEvaluator", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_document_map_evaluator_example()
