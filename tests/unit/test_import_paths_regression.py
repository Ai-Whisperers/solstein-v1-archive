import importlib


def test_entrypoint_modules_resolve() -> None:
    api_main = importlib.import_module("solstein.api.main")
    worker = importlib.import_module("solstein.worker")

    assert hasattr(api_main, "app")
    assert hasattr(worker, "run_worker")


def test_legacy_and_application_paths_resolve() -> None:
    modules = [
        "solstein.analytics.filters.llm",
        "solstein.application.analytics.filters.llm",
        "solstein.exporters.llm",
        "solstein.application.exporters.llm",
        "solstein.agents.github_agent",
        "solstein.application.agents.github_agent",
        "solstein.agents.web_search_agent",
        "solstein.application.agents.web_search_agent",
        "solstein.agents.companies_house_agent",
        "solstein.application.agents.companies_house_agent",
    ]

    for module_path in modules:
        imported = importlib.import_module(module_path)
        assert imported is not None
