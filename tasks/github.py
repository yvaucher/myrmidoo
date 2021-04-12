from contextlib import contextmanager

import logging
import github3

# from . import config
token = 'XXX'

_logger = logging.getLogger(__name__)


class Topics(object):
    business = "business"
    odoo_project = "odoo-project"
    docker = "docker"
    version = "odoo-"  # version will be appended
    mig_version = "odoo-mig-"  # version will be appended
    buildout = "buildout"
    need_5_digits = "need-5-digits"
    using_obsolete_docker_image = "using-obsolete-docker-image"
    on_pause = "on-pause"

    @classmethod
    def version_for(cls, version):
        return f"{cls.version}{version}"


@contextmanager
def login():
    """GitHub login as decorator so a pool can be implemented later."""
    yield github3.login(token=token)  # config.GITHUB_TOKEN)


def has_topic(repository, topic):
    return topic in repository.topics().names


def _exclude(repository, exclude_topics):
    for t in exclude_topics:
        if has_topic(repository, t):
            return True
    return False


def repositories_by_topic(org, topics, exclude_topics, include_archived=False):
    with login() as gh:
        topics = " ".join("topic:{}".format(t) for t in topics)
        gh_filter = " ".join([f"org:{org}", topics])
        for repo in gh.search_repositories(gh_filter):
            if not include_archived and repo.archived:
                continue
            if _exclude(repo.repository, exclude_topics):
                continue
            yield repo.repository


def repo_has_topic(gh_repo, topic):
    if not gh_repo:
        return False
    return has_topic(gh_repo, topic)


@contextmanager
def repository(org, repo):
    with login() as gh:
        try:
            yield gh.repository(org, repo)
        except github3.exceptions.NotFoundError:
            # no access right on the repo
            _logger.info("repo: %s/%s not found", org, repo)
            yield None
