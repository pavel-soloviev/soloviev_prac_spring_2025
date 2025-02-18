import os
import sys
import zlib

def get_branches(repo_path):
    refs_path = os.path.join(repo_path, ".git", "refs", "heads")
    if not os.path.exists(refs_path):
        print("Such directory does not exist")
        return
    for branch in os.listdir(refs_path):
        print(branch)


def get_last_commit(repo_path, branch_name):
    branch_ref_path = os.path.join(repo_path, ".git", "refs", "heads", branch_name)
    
    if os.path.exists(branch_ref_path):
        with open(branch_ref_path, "r") as f:
            commit_hash = f.read().strip()
        return commit_hash


def get_last_commit_info(repo_path, branch_name):
    commit_hash = get_last_commit(repo_path, branch_name)
    if not commit_hash:
        return None

    objects_dir = os.path.join(repo_path, ".git", "objects")
    commit_path = os.path.join(objects_dir, commit_hash[:2], commit_hash[2:])

    with open(commit_path, "rb") as f:
        compressed_data = f.read()
    decompressed_data = zlib.decompress(compressed_data).decode("utf-8")

    return decompressed_data

repo_path = sys.argv[1]
if len(sys.argv) == 2:
    get_branches(repo_path)
elif len(sys.argv) == 3:
    branch_name = sys.argv[2]
    print("Choose option")
    print(" 1 - Get last commit info\n", "2 - Get tree from last commit\n", "3 - Get history")
    
    option = input()
    match option:
        case "1":
            print(get_last_commit_info(repo_path, branch_name))



