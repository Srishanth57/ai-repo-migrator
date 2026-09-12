from unittest.mock import patch, MagicMock
from llm import get_migration_patch

@patch("llm.client.models.generate_content")
def test_get_migration_patch_returns_text(mock_generate):
    mock_response = MagicMock()
    mock_response.text = "def foo(): pass"
    mock_generate.return_value = mock_response
    result = get_migration_patch("old code", "upgrade to python3")
    assert "def foo" in result