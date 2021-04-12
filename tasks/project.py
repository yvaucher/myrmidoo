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


def _git_pull(org_name, gh_repo, branch="master", dest_dir=None):
    print("Pull {}".format(gh_repo.name))
    dest_dir = dest_dir or DOCKER_PROJECT_PATH
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    local_copy = os.path.join(dest_dir, gh_repo.name)
    if os.path.exists(local_copy):
        os.chdir(local_copy)
        subprocess.call(["git", "pull"])
    else:
        os.chdir(dest_dir)
        gh_address = "git@github.com:{}".format(gh_repo.full_name)
        subprocess.call(["git", "clone", gh_address])


@task(name="pull")
def pull(
    ctx,
    org_name="camptocamp",
    repo_name=None,
    branch=None,
    include_topics=None,
    exclude_topics=None,
    dest_dir=None,
):
    """Pull projects from GitHub to local directory.

    If the project doesn't exists it will clone it locally otherwise it will
    pull it. The default destination is in `~/.cache/myrmidoo/docker-projects`
    to provide info to `addons.ls` command.

    All projects pulled will be sub-directories of the destination directory.

    :param ctx:
    :param org_name: GitHub user to pull from (Default: camptocamp)
    :param repo_name: To pull a single repository
    :param branch: Target a specific branch (Default: master)
    :param include_topics: White list filter topics, only projects that includes
                           this topic will be pulled.
    :param exclude_topics: Black list filter topics, if a topic is present the
                           project won't be pulled.
    :param dest_dir: Destination directory on local storage where to download
                        or update the clones.
                        (Default: ~/.cache/myrmidoo/docker-projects)
    """
    # TODO pull only odoo/migration.yml
    # git checkout origin/master -- odoo/migration.yml
    ensure_project_dir()
    if include_topics:
        include_topics = include_topics.split(",")
    if exclude_topics:
        exclude_topics = exclude_topics.split(",")

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
            for t in include_topics:
                if not repo_has_topic(gh_repo, t):
                    _logger.info(
                        "repo: %s/%s excluded because topics do not have %s tag",
                        org_name,
                        repo_name,
                        t,
                    )
                    return
            for t in exclude_topics:
                if repo_has_topic(gh_repo, t):
                    _logger.info(
                        "repo: %s/%s excluded because topics have %s",
                        org_name,
                        repo_name,
                        t,
                    )
                    return

        _git_pull(org_name, gh_repo, branch=branch, dest_dir=dest_dir)
    else:
        topics = [Topics.odoo_project]
        if include_topics:
            topics.extend(include_topics)
        for gh_repo in github.repositories_by_topic(org_name, topics):
            if not repo_has_topic(gh_repo, Topics.docker):
                continue
            _git_pull(org_name, gh_repo, branch=branch, dest_dir=dest_dir)


def _ls(org_name="camptocamp"):
    for gh_repo in github.repositories_by_topic(org_name, [Topics.odoo_project]):
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
