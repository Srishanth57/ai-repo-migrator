import subprocess, tempfile, shutil, os

def run_tests_in_docker(repo_path: str) -> tuple[bool, str]:
    tmp = tempfile.mkdtemp()
    shutil.copytree(repo_path, tmp, dirs_exist_ok=True)
    result = subprocess.run(
        ["docker", "run", "--rm", "-v", f"{tmp}:/app", "-w", "/app",
         "python:3.11-slim", "sh", "-c", "pip install -q pytest && pytest -q"],
        capture_output=True, text=True, timeout=60
    )
    return result.returncode == 0, result.stdout + result.stderr