import shutil
from pathlib import Path

MOOD_DIR = Path("mood")
LOCALES_DIR = Path("mood/locales")
PO_FILE = LOCALES_DIR / "ru_RU/LC_MESSAGES/MUD.po"
MO_FILE = LOCALES_DIR / "ru_RU/LC_MESSAGES/MUD.mo"
DOCS_DIR = Path("docs")
BUILD_DIR = DOCS_DIR / "_build"
SRC_FILES = [
    "mood/server/__main__.py",
    "mood/client/__main__.py",
    "mood/common/__init__.py"
]
DOIT_CONFIG = {'default_tasks': ['html']}


def task_pot():
    """Создать .pot файл из исходников"""
    return {
        'actions': [
            f"pybabel extract -o {MOOD_DIR}/MUD.pot {' '.join(SRC_FILES)}",
        ],
        'file_dep': SRC_FILES,
        'targets': [f"{MOOD_DIR}/MUD.pot"],
        'clean': True,
    }


def task_po():
    """Обновить .po файл из .pot"""
    return {
        'actions': [
            f"pybabel update -D MUD -i {MOOD_DIR}/MUD.pot -d {LOCALES_DIR} -l ru_RU",
        ],
        'file_dep': [f"{MOOD_DIR}/MUD.pot"],
        'targets': [PO_FILE],
    }


def task_mo():
    """Скомпилировать .mo файл из .po"""
    return {
        'actions': [
            f"pybabel compile -D MUD -l ru_RU -i {PO_FILE} -d {LOCALES_DIR}",
        ],
        'file_dep': [PO_FILE],
        'targets': [MO_FILE],
        'clean': True,
    }


def task_html():
    """Генерация HTML документации"""
    return {
        'actions': [
            f'sphinx-build -M html {DOCS_DIR} {BUILD_DIR}',
        ],
        'file_dep': SRC_FILES,
        'targets': [BUILD_DIR],
        'clean': [lambda: shutil.rmtree(BUILD_DIR) if BUILD_DIR.exists() else None],
    }


def task_i18n():
    """Полная генерация перевода одним заданием"""
    return {
        'actions': [],
        'task_dep': ['pot', 'po', 'mo'],
    }


def task_test():
    """Запуск тестов"""
    return {
        'actions': [
            "python -m unittest discover -s unittests -p 'test_*.py' -v",
        ],
        'file_dep': [MO_FILE] + SRC_FILES,
        'task_dep': ['i18n'],
        'verbosity': 2,
        'uptodate': [False]
    }
