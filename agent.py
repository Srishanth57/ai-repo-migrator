import os
import difflib
from llm import get_migration_patch
from sandbox import run_tests_in_docker

def migrate(filepath, instruction, max_retries=2):
    with open(filepath) as f:
        original = f.read()

    error_feedback = ""
    repo_dir = os.path.dirname(filepath)

    for attempt in range(max_retries + 1):
        # Pass the code to LLM. 
        new_code = get_migration_patch(original, instruction, error_feedback)

        with open(filepath, "w") as f:
            f.write(new_code)

        passed, log = run_tests_in_docker(repo_dir)
        if passed:
            diff_text = "\n".join(difflib.unified_diff(
                original.splitlines(), new_code.splitlines(),
                fromfile="before", tofile="after", lineterm=""
            ))
            print(diff_text)
            confirm = input("Apply this change? (y/n): ")
            if confirm.lower() != "y":
                with open(filepath, "w") as f:
                    f.write(original)
                print("Change discarded, original file restored.")
                return None

            print("✅ Change applied and kept.")
            return new_code

        error_feedback = log

    with open(filepath, "w") as f:
        f.write(original)
    raise RuntimeError(f"Migration failed after {max_retries} retries.\nLast error:\n{error_feedback}")