# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from invoke import exceptions

import os
import appdirs

APP_NAME = "myrmidoo"
PROJECT_DIR = "docker-projects"


def cache_dir():
    return os.environ.get("MYRMIDOO_CACHE_DIR") or appdirs.user_cache_dir(APP_NAME)


def ensure_cache_dir():
    """Create cache directory if it doesn't exist"""
    directory = cache_dir()
    if not os.path.exists(directory):
        os.makedirs(directory)


def ensure_project_dir():
    """Create project directory if it doesn't exist"""
    directory = os.path.join(cache_dir(), PROJECT_DIR)
    if not os.path.exists(directory):
        os.makedirs(directory)


def exit_msg(message):
    """Print message and exit."""
    print(message)
    raise exceptions.Exit(1)
