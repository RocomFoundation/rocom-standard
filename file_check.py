import os
import json
import argparse

_DEFAULT_RELATIVE = "illegal.json"
_SPEC_DIR = "spec"

def _resolve_registry_path() -> str:
    """Resolve registry path — works both locally and inside Docker."""
    candidates = [
        # Environment variable (for container deployments)
        os.path.join(os.environ.get('ROCOM_SPECS_DIR', '')),
        # Inside Docker container (specs volume → standards submodule)
        "/app/illegal.json",
        # Local dev from repo root
        _DEFAULT_RELATIVE,
        os.path.join(os.path.expanduser("~"), "Rocom", "illegal.json"),
    ]
    # Walk up from this module to find specs/
    current = os.path.dirname(os.path.abspath(__file__))
    for _ in range(10):
        candidate = os.path.join(current, _DEFAULT_RELATIVE)
        candidates.append(candidate)
        current = os.path.dirname(current)

    for path in candidates:
        if os.path.isfile(path):
            return path
    raise FileNotFoundError(
        f"Cannot find {_DEFAULT_RELATIVE}. Searched: {candidates}"
    )

def load_illegal_phrases(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("phrases", [])

def is_text_file(filepath: str) -> bool:
    """Skip binary files by checking extension."""
    text_extensions = {".md", ".txt", ".py", ".json", ".yaml", ".yml", ".cpp", ".h", ".c", ".hpp", ""}
    return os.path.splitext(filepath)[1].lower() in text_extensions

def scan_file(filepath: str, phrases: list[str], case_sensitive: bool) -> list[tuple[int, str]]:
    """Return list of (line_number, phrase) for matches in filepath."""
    matches = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, start=1):
                for phrase in phrases:
                    search_phrase = phrase if case_sensitive else phrase.lower()
                    search_line = line if case_sensitive else line.lower()
                    if search_phrase in search_line:
                        matches.append((line_num, phrase))
    except (UnicodeDecodeError, PermissionError, OSError):
        return []
    return matches

def set_env_variables(value: str):
    output_file = os.getenv('GITHUB_OUTPUT')
    val = value
    with open(output_file, "a") as env_file:
        env_file.write(f"FILE_CHECK={val}")

def main():
    parser = argparse.ArgumentParser(description="Scan spec/ for illegal phrases.")
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help="Match phrases case-sensitively (default: case-insensitive).",
    )
    parser.add_argument(
        "--dir",
        default=_SPEC_DIR,
        help=f"Directory to scan (default: {_SPEC_DIR}).",
    )
    args = parser.parse_args()

    phrases_path = _resolve_registry_path()
    phrases = load_illegal_phrases(phrases_path)
    if not phrases:
        print("No phrases defined in illegal.json.")
        return

    scan_dir = args.dir
    if not os.path.isdir(scan_dir):
        print(f"Directory not found: {scan_dir}")
        return

    total_matches = 0
    for root, _, files in os.walk(scan_dir):
        for filename in files:
            filepath = os.path.join(root, filename)
            if not is_text_file(filepath):
                continue
            matches = scan_file(filepath, phrases, args.case_sensitive)
            for line_num, phrase in matches:
                rel_path = os.path.relpath(filepath, scan_dir)
                print(f"{rel_path}:{line_num}:{phrase}")
                total_matches += 1

    if total_matches == 0:
        print("No illegal phrases found.")
        set_env_variables("TRUE")
        return True
    else:
        print(f"\nFound {total_matches} match(es).")
        set_env_variables("FALSE")
        return False

if __name__ == "__main__":
    main()