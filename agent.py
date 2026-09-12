import difflib
from llm import get_migration_patch
from sandbox import run_tests_in_docker

def migrate(filepath, instruction, max_retries=2):
    with open(filepath) as f:
        original = f.read()

    error_feedback = ""
    for attempt in range(max_retries + 1):
        patch = get_migration_patch(original, instruction, error_feedback)
        # naive apply for MVP: ask Gemini to return FULL new file instead of diff (simpler to implement in your time budget)
        new_code = patch  # if you prompt it to return full file content instead of a diff
        with open(filepath + ".tmp", "w") as f:
            f.write(new_code)

        passed, log = run_tests_in_docker(os.path.dirname(filepath))
        if passed:
            diff = difflib.unified_diff(original.splitlines(), new_code.splitlines(), lineterm="")
            print("\n".join(diff))
            return new_code
        error_feedback = log
    raise RuntimeError("Migration failed after retries")