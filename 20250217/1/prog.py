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

if len(sys.argv) == 2:
    repo_path = sys.argv[1]
    get_branches(repo_path)
