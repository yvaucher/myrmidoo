# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from invoke import exceptions


def exit_msg(message):
    """Print message and exit."""
    print(message)
    raise exceptions.Exit(1)
