from pathlib import Path

HERE = Path(__file__).resolve().parent


def test_exact_marker_and_shutdown_contract() -> None:
    shared = (HERE / "_shared.py").read_text()
    assert "override=False" in shared
    assert 'os.getenv("RESPAN_EXAMPLE_RUN_ID")' in shared
    assert '"example_run_id": example_run_id()' in shared
    for path in HERE.glob("0[1-4]_*.py"):
        assert "respan.shutdown()" in path.read_text()


def test_runner_aggregates_timeouts_and_failures() -> None:
    source = (HERE / "run_all.py").read_text()
    assert "check=False" in source
    assert "timeout=120" in source
    assert "failures.append" in source


def test_examples_use_real_installed_manager_types() -> None:
    source = (HERE / "_shared.py").read_text()
    assert "weaviate.collections.collections.sync" in source
    assert "weaviate.collections.data.async_" in source
    assert "weaviate.collections.query" in source


def test_live_example_is_credential_gated() -> None:
    source = (HERE / "04_live_service.py").read_text()
    assert 'os.getenv("WEAVIATE_URL")' in source
    assert 'os.getenv("WEAVIATE_API_KEY")' in source
    assert "connect_to_weaviate_cloud" in source
