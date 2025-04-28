from pathlib import Path
import zipfile

DOIT_CONFIG = {'default_tasks': ['docs']}

def task_docs():
    """Build documentation"""
    deps = [*Path(".").glob("*.py"), *Path(".").glob("*.rst")]
    for kind in ("html", "text"):
        yield {
               "name": kind,
               "file_dep": deps,
               "actions": [f"sphinx-build -M {kind} ./source/ _build"],
    }

def task_erasea():
    """erase all gener and new files"""
    return {
            "actions": ["git reset --hard", "git clean -xdf"]
    }

def task_zip():
    """Make zip archive from documentation"""
    return {
            "actions": ["zip -r docs.zip _build/html"],
            "task_dep": ["docs"],
    }

def task_stat():
    """Stat"""
    return {
            "actions": [f"python3 -m zipfile -l docs.zip > docs.list"],
            "file_dep": ["docs.zip"],
            "targets": ["docs.list"],
    }

def list_zip_contents(zip_path, output_file):
    with zipfile.ZipFile(zip_path, 'r') as zf:
        for file_info in zf.infolist():
            print(f"{file_info.filename.ljust(40)} {file_info.file_size:>10}", file=output_file)

def task_stat1():
    return {
            "actions": [(list_zip_contents, ["_build/html", "docs1.list"])],
            "targets": ["docs1.list"],
    }

