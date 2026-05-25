"""One-script example for DocumentNDCGEvaluator."""

from _shared import configure_respan, finish_respan, print_result


def run_document_ndcg_evaluator_example():
    respan = configure_respan("haystack-document-ndcg-evaluator")
    try:
        from haystack import Document
        from haystack.components.evaluators import DocumentNDCGEvaluator

        relevant = [Document(content="A"), Document(content="B")]
        retrieved = [Document(content="C"), relevant[0], relevant[1]]
        result = DocumentNDCGEvaluator().run(
            ground_truth_documents=[relevant],
            retrieved_documents=[retrieved],
        )
        print_result("DocumentNDCGEvaluator", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_document_ndcg_evaluator_example()
