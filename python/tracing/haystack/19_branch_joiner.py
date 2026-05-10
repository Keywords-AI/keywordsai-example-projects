"""One-script example for BranchJoiner."""

from _shared import configure_respan, finish_respan, print_result


def run_branch_joiner_example():
    respan = configure_respan("haystack-branch-joiner")
    try:
        from haystack.components.joiners import BranchJoiner

        result = BranchJoiner(str).run(value=["selected branch"])
        print_result("BranchJoiner", result)
        return result
    finally:
        finish_respan(respan)


if __name__ == "__main__":
    run_branch_joiner_example()
