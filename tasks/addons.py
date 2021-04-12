# Copyright 2019-2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import yaml
import os
import pandas
from tabulate import tabulate

from invoke import task

from collections import defaultdict

from .common import exit_msg, ensure_cache_dir, cache_dir
from . import project as project_task

MIG_FPATH = os.path.join("odoo", "migration.yml")
VERSION_FPATH = os.path.join("odoo", "VERSION")
LOCAL_SRC_PATH = os.path.join("odoo", "local-src")
DOCKER_PROJECT_PATH = os.path.join(cache_dir(), "docker-projects")


def _get_local_src(project):
    """ List all modules in local project directory.
    """

    local_src = os.path.join(project, LOCAL_SRC_PATH)
    return os.listdir(local_src)


def _get_OCA_addons(version):
    """ Read from <cache>/oca/*/{version}-addons list

    """
    # TODO create the addons lists
    return []


def _get_CE_addons(version):
    """ Read from <cache>/odoo/odoo/*/{version}-addons list

    """
    # TODO create the addons lists
    fname = os.path.join(cache_dir(), "odoo", "odoo", version + "-addons")
    if not os.path.isfile(fname):
        return []
    with open(fname) as f:
        return f.read().splitlines()


def _get_EE_addons(version):
    fname = os.path.join(cache_dir(), "odoo", "enterprise", version + "-addons")
    if not os.path.isfile(fname):
        return []
    with open(fname) as f:
        return f.read().splitlines()


def _get_project_list():
    list_fp = os.path.join(cache_dir(), "project.list")
    if os.path.exists(list_fp):
        with open(list_fp) as f:
            return f.read().splitlines()
    else:
        print("Generating project list into {}".format(list_fp))

        projects = []
        with open(list_fp, "a") as f:
            for project_name in project_task._ls():
                f.write(project_name + "\n")
                projects.append(project_name)
        return projects


def _get_raw_addon_list():
    """
    @returns DataFrame containing addons data

    """
    addons = []

    projects = _get_project_list()
    project_errors = {}

    project_dir = DOCKER_PROJECT_PATH
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)

    for p in projects:
        project_path = os.path.join(project_dir, p)

        local_addons = _get_local_src(project_path)
        with open(os.path.join(project_path, VERSION_FPATH)) as version:
            v = version.read().split(".")
            if len(v) == 3:
                v = "{}.0".format(v[0])
            elif len(v) == 5:
                v = ".".join(v[:2])
            else:
                # Unknown format
                message = ("Project {} has an unknown version format:\n{}").format(p, v)
                project_errors[p] = message
                continue

        oca_addons = _get_OCA_addons(v)
        ce_addons = _get_CE_addons(v)
        ee_addons = _get_EE_addons(v)
        # TODO consider other as 'misc'

        with open(os.path.join(project_path, MIG_FPATH)) as mig:
            # content = yaml.load(mig, Loader=yaml.FullLoader)
            content = yaml.load(mig)
            # TODO _check_format(content)
            versions = content["migration"]["versions"]
            # get first step
            setup = versions[0]
            if setup.get("version") == "migration":
                setup = versions[1]
            installed_addons = setup["addons"]["upgrade"]
            for a in installed_addons:
                org = "undefined"
                if a in local_addons:
                    org = "c2c"
                elif a in oca_addons:
                    org = "oca"
                elif a in ce_addons:
                    org = "CE"
                elif a in ee_addons:
                    org = "EE"
                addons.append([a, p, v, org, "none"])

    labels = ["addon", "project", "version", "org", "platform"]
    df = pandas.DataFrame(addons, columns=labels)
    if project_errors:
        exit_msg(project_errors)
    return df


def _ls(
    filter_org=None,
    reverse=False,
    groupby_addon=False,
    groupby_version=False,
    sort_count=True,
    table_fmt="presto",
):
    df = _get_raw_addon_list()

    if filter_org:
        orgs = filter_org.split(",")
        df = df.loc[df["org"].isin(orgs)]

    groupby = []
    if groupby_addon:
        groupby.append("addon")
    if groupby_version:
        groupby.append("version")
    if groupby:
        # when only grouping by addon we can show org
        if groupby == ["addon"]:
            groupby.append("org")
        df = df.groupby(groupby).size().reset_index(name="count")
        if sort_count:
            sort_by = ["count"]
            ascending = [reverse]
            if "addon" in groupby:
                df = df.sort_values(by="addon", ascending=reverse)
                sort_by.append("addon")
                ascending.append(not reverse)
            df = df.sort_values(by=sort_by, ascending=ascending)
            # TODO get rid of previous index column (index is unordered ofter
            # sort)

    # keep 0 in versions
    floatfmt = ".1f"

    return tabulate(df, floatfmt=floatfmt, headers="keys", tablefmt=table_fmt)


@task(name="ls")
def ls(
    ctx,
    filter_org=None,
    reverse=False,
    groupby_addon=False,
    groupby_version=False,
    sort_count=True,
    table_fmt="presto",
):
    """ task to get addons list
    Print a table of addons

    With columns (project, version, addon org, platform type)

    Addon org can be OCA, c2c, core, enterprise

    @param filter_org: Filter on org
    @param reverse: reverse table order (counts are DESC by default)
    @param groupby_addon: Group count by addon name
    @param groupby_version: Group count by version
    @param sort_count: When using groupby counter, sort by count (Default True)
    @param table_fmt: Output format of the table (tabulate format)

    """
    ensure_cache_dir()
    print(
        _ls(
            filter_org=filter_org,
            reverse=reverse,
            groupby_addon=groupby_addon,
            groupby_version=groupby_version,
            table_fmt=table_fmt,
        )
    )
