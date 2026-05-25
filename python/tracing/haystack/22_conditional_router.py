"""One-script example for ConditionalRouter."""

from _shared import configure_respan, finish_respan, print_result


def run_conditional_router_example():
    respan = configure_respan("haystack-conditional-router")
    try:
        from haystack.components.routers import ConditionalRouter

        routes = [
            {
                "condition": "{{ query | length <= 12 }}",
                "output": "{{ query }}",
                "output_name": "short_query",
                "output_type": str,
            },
            {
                "condition": "{{ True }}",
                "output": "{{ query }}",
                "output_name": "long_query",
                "output_type": str,
            },
        ]
        result = ConditionalRouter(routes).run(query="short")
        print_result("ConditionalRouter", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_conditional_router_example()
