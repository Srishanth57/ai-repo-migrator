from unittest.mock import patch
from llm import get_migration_patch

@patch("llm.model.generate_content")
def test_get_migration_patch_returns_text(mock_generate):
    mock_generate.return_value.text = "def foo(): pass"
    result = get_migration_patch("old code", "upgrade to python3")
    assert "def foo" in result