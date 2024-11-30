import os
import hashlib
import json
import shutil

MYGIT_DIR = ".mygit"

def init():
    """Initialize a new repository."""
    if os.path.exists(MYGIT_DIR):
        print("Repository already initialized.")
        return
    os.makedirs(f"{MYGIT_DIR}/objects")
    os.makedirs(f"{MYGIT_DIR}/refs/heads")
    with open(f"{MYGIT_DIR}/HEAD", "w") as f:
        f.write("refs/heads/main")
    with open(f"{MYGIT_DIR}/index", "w") as f:
        f.write("{}")  # Empty index
    print("Initialized empty repository.")


def hash_object(data):
    """Generate a SHA-1 hash for a given data string."""
    return hashlib.sha1(data.encode()).hexdigest()


def add(file_path):
    """Stage a file."""
    if not os.path.exists(MYGIT_DIR):
        print("Not a repository.")
        return
    with open(file_path, "r") as f:
        content = f.read()
    file_hash = hash_object(content)
    
    # Save blob
    obj_path = f"{MYGIT_DIR}/objects/{file_hash}"
    if not os.path.exists(obj_path):
        with open(obj_path, "w") as f:
            f.write(content)
    
    # Update index
    with open(f"{MYGIT_DIR}/index", "r") as f:
        index = json.load(f)
    index[file_path] = file_hash
    with open(f"{MYGIT_DIR}/index", "w") as f:
        json.dump(index, f)
    print(f"Staged {file_path}.")



def commit(message):
    """Create a new commit."""
    if not os.path.exists(MYGIT_DIR):
        print("Not a repository.")
        return
    with open(f"{MYGIT_DIR}/index", "r") as f:
        index = json.load(f)
    
    # Create tree object (representing directory structure)
    tree_hash = hash_object(json.dumps(index))
    obj_path = f"{MYGIT_DIR}/objects/{tree_hash}"
    with open(obj_path, "w") as f:
        json.dump(index, f)
    
    # Get current branch
    with open(f"{MYGIT_DIR}/HEAD", "r") as f:
        branch = f.read().strip()
    
    # Get parent commit
    branch_path = f"{MYGIT_DIR}/{branch}"
    parent = None
    if os.path.exists(branch_path):
        with open(branch_path, "r") as f:
            parent = f.read().strip()
    
    # Create commit object
    commit_data = {
        "tree": tree_hash,
        "parent": parent,
        "message": message
    }
    commit_hash = hash_object(json.dumps(commit_data))
    with open(f"{MYGIT_DIR}/objects/{commit_hash}", "w") as f:
        json.dump(commit_data, f)
    
    # Update branch
    with open(branch_path, "w") as f:
        f.write(commit_hash)
    print(f"Committed: {message}.")



def log():
    """Show commit history."""
    if not os.path.exists(MYGIT_DIR):
        print("Not a repository.")
        return
    with open(f"{MYGIT_DIR}/HEAD", "r") as f:
        branch = f.read().strip()
    branch_path = f"{MYGIT_DIR}/{branch}"
    if not os.path.exists(branch_path):
        print("No commits yet.")
        return
    commit_hash = open(branch_path).read().strip()
    while commit_hash:
        with open(f"{MYGIT_DIR}/objects/{commit_hash}", "r") as f:
            commit_data = json.load(f)
        print(f"Commit: {commit_hash}\nMessage: {commit_data['message']}\n")
        commit_hash = commit_data["parent"]



def branch(name):
    """Create a new branch."""
    if not os.path.exists(MYGIT_DIR):
        print("Not a repository.")
        return
    with open(f"{MYGIT_DIR}/HEAD", "r") as f:
        current_branch = f.read().strip()
    current_commit = open(f"{MYGIT_DIR}/{current_branch}").read().strip()
    with open(f"{MYGIT_DIR}/refs/heads/{name}", "w") as f:
        f.write(current_commit)
    print(f"Branch {name} created.")
