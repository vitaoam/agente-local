from app.services.app_registry import resolve_app, list_supported_apps


def test_resolve_paint():
    assert resolve_app("paint") == "mspaint"


def test_resolve_bloco_de_notas():
    assert resolve_app("bloco de notas") == "notepad"


def test_resolve_notepad():
    assert resolve_app("notepad") == "notepad"


def test_resolve_calculadora():
    assert resolve_app("calculadora") == "calc"


def test_resolve_explorer():
    assert resolve_app("explorer") == "explorer"


def test_resolve_unknown_app():
    assert resolve_app("app_inexistente") is None


def test_resolve_empty_string():
    assert resolve_app("") is None


def test_case_insensitive():
    assert resolve_app("Paint") == "mspaint"
    assert resolve_app("NOTEPAD") == "notepad"
    assert resolve_app("Calculadora") == "calc"


def test_whitespace_handling():
    assert resolve_app("  paint  ") == "mspaint"
    assert resolve_app(" notepad ") == "notepad"


def test_list_supported_apps():
    apps = list_supported_apps()
    assert isinstance(apps, list)
    assert len(apps) > 0
    assert "paint" in apps
    assert "notepad" in apps
    assert "calculadora" in apps
