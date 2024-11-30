import os
import hashlib
import json
import time
import argparse
from pathlib import Path

REPO_DIR = ".myscm"


def init():
    """Initialize a repository."""
    if not os.path.exists(REPO_DIR):
        os.makedirs(REPO_DIR)
        os.makedirs(f"{REPO_DIR}/objects")
        os.makedirs(f"{REPO_DIR}/refs/heads")  # Create directory for branch heads
        with open(f"{REPO_DIR}/HEAD", "w") as head:
            head.write("refs/heads/main\n")
        # Create an initial branch file for 'main'
        with open(f"{REPO_DIR}/refs/heads/main", "w") as main_branch:
            main_branch.write("")  # Start with no commits
        print("Repository initialized.")
    else:
        print("Repository already exists.")

# This function cmputes the SHA-1 hash of the given data and stores it in the objects directory.
def hash_object(data):
    """Hash and store an object."""
    sha1 = hashlib.sha1(data).hexdigest()
    path = f"{REPO_DIR}/objects/{sha1}"
    with open(path, "wb") as f:
        f.write(data)
    return sha1

# This function loads the index file, which keeps track of the staged changes.
def add(file_path):
    """Stage a file."""
    if not os.path.exists(REPO_DIR):
        print("Not a repository. Run `init` first.")
        return

    if is_ignored(file_path):
        print(f"File '{file_path}' is ignored.")
        return

    with open(file_path, "rb") as f:
        data = f.read()
    sha1 = hash_object(data)

    index = load_index()
    index[file_path] = sha1
    save_index(index)
    print(f"Staged '{file_path}'.")

# This function creates a new commit based on the staged files
def commit(message):
    """Create a new commit."""
    index = load_index()
    if not index:
        print("Nothing to commit.")
        return

    commit_data = {
        "tree": index,
        "message": message,
        "parent": get_current_commit(),
        "timestamp": time.time(),
    }
    commit_hash = hash_object(json.dumps(commit_data).encode())

    branch = get_current_branch()
    with open(f"{REPO_DIR}/{branch}", "w") as branch_file:
        branch_file.write(commit_hash)

    clear_index()
    print(f"Committed as {commit_hash}")

# This functcion displays the history of commits 
def log():
    """Show commit history."""
    current_commit = get_current_commit()
    while current_commit:
        commit_data = load_object(current_commit)
        print(f"Commit: {current_commit}")
        print(f"Message: {commit_data['message']}")
        print(f"Timestamp: {time.ctime(commit_data['timestamp'])}\n")
        current_commit = commit_data["parent"]

# This function checks if a file should be ignored based on patterns specified in a .myscmignore file.
def is_ignored(file_path):
    """Check if a file is ignored."""
    if not os.path.exists(".myscmignore"):
        return False
    with open(".myscmignore") as f:
        ignored_patterns = f.read().splitlines()
    return any(Path(file_path).match(pattern) for pattern in ignored_patterns)


# Helper functions
def load_index():
    index_path = f"{REPO_DIR}/index"
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            return json.load(f)
    return {}


def save_index(index):
    index_path = f"{REPO_DIR}/index"
    with open(index_path, "w") as f:
        json.dump(index, f)


def clear_index():
    save_index({})


def get_current_branch():
    with open(f"{REPO_DIR}/HEAD") as f:
        return f.read().strip()


def get_current_commit():
    branch = get_current_branch()
    branch_path = f"{REPO_DIR}/{branch}"
    if os.path.exists(branch_path):
        with open(branch_path) as f:
            return f.read().strip()
    return None


def load_object(sha1):
    path = f"{REPO_DIR}/objects/{sha1}"
    with open(path, "r") as f:
        return json.loads(f.read())


# CLI setup and setups up argument parsing for vaiouse commands (init, add, commit, log) enabling user interaaction through the command line.
def main():
    parser = argparse.ArgumentParser(description="A simple version control system")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    subparsers.add_parser("init", help="Initialize a new repository")

    # add
    add_parser = subparsers.add_parser("add", help="Stage a file")
    add_parser.add_argument("file", help="File to stage")

    # commit
    commit_parser = subparsers.add_parser("commit", help="Commit staged changes")
    commit_parser.add_argument("message", help="Commit message")

    # log
    subparsers.add_parser("log", help="Show commit history")

    # Parse arguments
    args = parser.parse_args()

    # Command execution
    if args.command == "init":
        init()
    elif args.command == "add":
        add(args.file)
    elif args.command == "commit":
        commit(args.message)
    elif args.command == "log":
        log()


if __name__ == "__main__":
    main()