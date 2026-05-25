"""One-script example for TopPSampler."""

from _shared import configure_respan, finish_respan, print_result, sample_documents


def run_top_p_sampler_example():
    respan = configure_respan("haystack-top-p-sampler")
    try:
        try:
            from haystack.components.samplers import TopPSampler

            sampler = TopPSampler(top_p=0.8, min_top_k=1)
            result = sampler.run(sample_documents())
        except ImportError as exc:
            result = {
                "skipped": "TopPSampler requires the optional torch dependency.",
                "error": str(exc),
            }
        print_result("TopPSampler", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_top_p_sampler_example()
