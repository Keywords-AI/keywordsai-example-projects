"""One-script example for CacheChecker."""

from _shared import configure_respan, finish_respan, print_result, sample_document_store


def run_cache_checker_example():
    respan = configure_respan("haystack-cache-checker")
    try:
        from haystack.components.caching import CacheChecker

        checker = CacheChecker(sample_document_store(), cache_field="source")
        result = checker.run(["python", "missing"])
        print_result("CacheChecker", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_cache_checker_example()
