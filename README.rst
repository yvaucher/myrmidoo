:ant::ant::ant: Myrmidoo :ant::ant::ant:
=======


> A divine empowered creature to read in the Akashic records of our projects through the aether-net.


Simple tool to fetch and read infos from a bunch of projects using marabunta.
This tool can fetch infos from github using tags and read marabunta migration files.


invoke project.ls

    Get the list of project from github.

invoke project.pull

    Pull the list of project into .cache/myrmidoo/docker-projects

invoke addons.ls

    Print a table of addons

    With columns (project, version, addon org, platform type)

    Addon org can be OCA, c2c, core, enterprise

    --filter_org: Filter on org
    --reverse: reverse table order (counts are DESC by default)
    --groupby_addon: Group count by addon name
    --groupby_version: Group count by version
    --sort_count: When using groupby counter, sort by count (Default True)
    --table_fmt: Output format of the table (tabulate format)
