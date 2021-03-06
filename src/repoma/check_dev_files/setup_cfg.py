"""Apply a certain set of standards to the :file:`setup.cfg`."""

import os
import textwrap
from collections import defaultdict

from repoma.errors import PrecommitError
from repoma.format_setup_cfg import write_formatted_setup_cfg
from repoma.utilities import CONFIG_PATH
from repoma.utilities.cfg import copy_config
from repoma.utilities.executor import Executor
from repoma.utilities.setup_cfg import open_setup_cfg


def main(ignore_author: bool) -> None:
    if not CONFIG_PATH.setup_cfg.exists():
        return
    executor = Executor()
    executor(_check_required_options)
    if not ignore_author:
        executor(_update_author_data)
    executor(_fix_long_description)
    if executor.error_messages:
        raise PrecommitError(executor.merge_messages())


def _check_required_options() -> None:
    cfg = open_setup_cfg()
    required_options = {
        "metadata": [
            "name",
            "description",
            "license",
            "classifiers",
        ],
        "options": ["python_requires"],
    }
    missing_options = defaultdict(list)
    for section, options in required_options.items():
        for option in options:
            if cfg.has_option(section, option):
                continue
            missing_options[section].append(option)
    if missing_options:
        summary = "\n"
        for section, options in missing_options.items():
            summary += f"[{section}]\n...\n"
            for option in options:
                summary += f"{option} = ...\n"
            summary += "...\n"
        raise PrecommitError(
            f"./{CONFIG_PATH.setup_cfg} is missing the following options:\n"
            + textwrap.indent(summary, prefix="  ")
        )


def _update_author_data() -> None:
    old_cfg = open_setup_cfg()
    new_cfg = copy_config(old_cfg)
    new_cfg.set("metadata", "author", "Common Partial Wave Analysis")
    new_cfg.set("metadata", "author_email", "Common Partial Wave Analysis")
    new_cfg.set("metadata", "author_email", "compwa-admin@ep1.rub.de")
    if new_cfg != old_cfg:
        write_formatted_setup_cfg(new_cfg)
        raise PrecommitError(f"Updated author info in ./{CONFIG_PATH.setup_cfg}")


def _fix_long_description() -> None:
    if os.path.exists("README.md"):
        old_cfg = open_setup_cfg()
        new_cfg = copy_config(old_cfg)
        new_cfg.set("metadata", "long_description", "file: README.md")
        new_cfg.set("metadata", "long_description_content_type", "text/markdown")
        if new_cfg != old_cfg:
            write_formatted_setup_cfg(new_cfg)
            raise PrecommitError(
                f"Updated long_description in ./{CONFIG_PATH.setup_cfg}"
            )
