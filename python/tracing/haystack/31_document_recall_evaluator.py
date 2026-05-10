"""One-script example for DocumentRecallEvaluator."""

from _shared import configure_respan, finish_respan, print_result


def run_document_recall_evaluator_example():
    respan = configure_respan("haystack-document-recall-evaluator")
    try:
        from haystack import Document
        from haystack.components.evaluators import DocumentRecallEvaluator

        relevant = [Document(content="A"), Document(content="B")]
        retrieved = [relevant[1], Document(content="C")]
        result = DocumentRecallEvaluator().run(
            ground_truth_documents=[relevant],
            retrieved_documents=[retrieved],
        )
        print_result("DocumentRecallEvaluator", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_document_recall_evaluator_example()
