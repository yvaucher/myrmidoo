import os

import github3
import logging
import subprocess

from . import github
from .github import repo_has_topic, Topics

from invoke import task

_logger = logging.getLogger(__name__)

def _git_pull(org_name, gh_repo, branch='master'):
    print("Pull {}".format(gh_repo.name))
    local_copy = '.data/docker-projects/{}'.format(gh_repo.name)
    if os.path.exists(local_copy):
        os.chdir(local_copy)
        subprocess.call(['git', 'pull'])
        os.chdir('../../..')
    else:
        os.chdir(".data/docker-projects")
        gh_address = "git@github.com:{}".format(gh_repo.full_name)
        subprocess.call(['git', 'clone', gh_address])
        os.chdir('../..')


@task(name='pull')
def pull(ctx, org_name='camptocamp', repo_name=None, branch=None):
    # TODO pull only odoo/migration.yml
    # git checkout origin/master -- odoo/migration.yml
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
        _git_pull(org_name, gh_repo, branch=branch)
    else:
        for gh_repo in github.repositories_by_topic(org_name, Topics.odoo_project):
            if not repo_has_topic(gh_repo, Topics.docker):
                continue
            _git_pull(org_name, gh_repo, branch=branch)


@task(name='ls')
def ls(ctx, org_name='camptocamp'):
    for gh_repo in github.repositories_by_topic(org_name, Topics.odoo_project):
        if not repo_has_topic(gh_repo, Topics.docker):
            continue
        print(gh_repo.name)
