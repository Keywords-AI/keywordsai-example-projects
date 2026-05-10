"""One-script example for DocumentMRREvaluator."""

from _shared import configure_respan, finish_respan, print_result


def run_document_mrr_evaluator_example():
    respan = configure_respan("haystack-document-mrr-evaluator")
    try:
        from haystack import Document
        from haystack.components.evaluators import DocumentMRREvaluator

        relevant = [Document(content="A"), Document(content="B")]
        retrieved = [Document(content="C"), relevant[1]]
        result = DocumentMRREvaluator().run(
            ground_truth_documents=[relevant],
            retrieved_documents=[retrieved],
        )
        print_result("DocumentMRREvaluator", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_document_mrr_evaluator_example()
