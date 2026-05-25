"""One-script example for ListJoiner."""

from _shared import configure_respan, finish_respan, print_result


def run_list_joiner_example():
    respan = configure_respan("haystack-list-joiner")
    try:
        from haystack.components.joiners import ListJoiner

        result = ListJoiner(int).run(values=[[1, 2], [3]])
        print_result("ListJoiner", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_list_joiner_example()
