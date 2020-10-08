import os

import github3
import logging
import subprocess

from . import github
from .common import ensure_cache_dir, ensure_project_dir, cache_dir
from .github import repo_has_topic, Topics

from invoke import task

_logger = logging.getLogger(__name__)

DOCKER_PROJECT_PATH = os.path.join(cache_dir(), "docker-projects")


def _git_pull(org_name, gh_repo, branch="master"):
    print("Pull {}".format(gh_repo.name))
    local_copy = os.path.join(DOCKER_PROJECT_PATH, gh_repo.name)
    if os.path.exists(local_copy):
        os.chdir(local_copy)
        subprocess.call(["git", "pull"])
        os.chdir("../../..")
    else:
        os.chdir(DOCKER_PROJECT_PATH)
        gh_address = "git@github.com:{}".format(gh_repo.full_name)
        subprocess.call(["git", "clone", gh_address])
        os.chdir("../..")


@task(name="pull")
def pull(ctx, org_name="camptocamp", repo_name=None, branch=None):
    # TODO pull only odoo/migration.yml
    # git checkout origin/master -- odoo/migration.yml
    ensure_project_dir()
    if repo_name:
        with github.repository(org_name, repo_name) as gh_repo:
            if not (
                repo_has_topic(gh_repo, Topics.odoo_project)
                and repo_has_topic(gh_repo, Topics.docker)
            ):
                _logger.info(
                    "repo: %s/%s excluded because topics do not have %s and %s",
                    org_name,
                    repo_name,
                    Topics.odoo_project,
                    Topics.docker,
                )
                return
            elif repo_has_topic(gh_repo, Topics.on_pause):
                _logger.info(
                    "repo: %s/%s excluded because topics have %s",
                    org_name,
                    repo_name,
                    Topics.on_pause,
                )
                return
        _git_pull(org_name, gh_repo, branch=branch)
    else:
        for gh_repo in github.repositories_by_topic(org_name, Topics.odoo_project):
            if not repo_has_topic(gh_repo, Topics.docker):
                continue
            _git_pull(org_name, gh_repo, branch=branch)


def _ls(org_name="camptocamp"):
    for gh_repo in github.repositories_by_topic(org_name, Topics.odoo_project):
        if not repo_has_topic(gh_repo, Topics.docker):
            continue
        yield gh_repo.name


@task(name="ls")
def ls(ctx, org_name="camptocamp"):
    """Lists the active projects

    NOTE: it requires a valid Github Token
    """
    for proj_name in _ls(org_name=org_name):
        print(proj_name)
