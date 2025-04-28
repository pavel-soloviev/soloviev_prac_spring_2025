def task_docs():
    """Build documentation"""
    return {
            "actions": ['sphinx-build -M html . _build']
    }

def task_erasea():
    """erase all gener and new files"""
    return {
            "actions": ["git reset --hard", "git clean -xdf"]
    }
