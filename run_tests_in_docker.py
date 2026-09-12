from unittest.mock import patch
from sandbox import run_tests_in_docker

@patch("sandbox.subprocess.run")
def test_run_tests_in_docker_calls_docker(mock_run):
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "1 passed"
    mock_run.return_value.stderr = ""
    passed, log = run_tests_in_docker("sample_repo")
    assert passed is True
    assert "docker" in mock_run.call_args[0][0]