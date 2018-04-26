#!/usr/bin/env python2

"""
This module is aimed at running saasherder parser to find
latest tag, git-url and image tag for given container repository.
"""

import subprocess
import logging

from command import run_cmd


SAASHERDER_PARSER_DIR = \
    "/opt/scanning/saasherder_parser/"

GET_REPO_SCRIPT = "./get_repo_details_from_image.sh"


def run_saasherder(repository):
    """
    Run saas herder parser on given repository and find out
    git-url and git-sha for image under test.
    Returns None if failed to parse using saasherder
    Returns dict = {"git_url": GIT_URL, "git_sha": GIT_SHA,
                    "image_tag": IMAGE_TAG} on success
    """
    cmd = "cd {} && {} {} && cd -".format(
        SAASHERDER_PARSER_DIR, GET_REPO_SCRIPT, repository)
    logger = logging.getLogger("weeklyscan")
    logger.info("Checking repo: {} via saasherder".format(repository))
    try:
        output = run_cmd(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        msg = "Error occurred processing saasherder for {}".format(repository)
        msg = msg + "\n{}".format(e)
        logger.warning(msg)
        return None
    else:
        # lets parse stdout
        try:
            # last 3 lines has git-url, git-sha and image-tag
            # we want -2 and -3 indexed elements
            lines = output.strip().split("\n")[-3:-1]
        except Exception as e:
            msg = "Error parsing saasherder output. {}".format(e)
            msg = msg + "Output: " + output
            logger.warning(msg)
            return None

        if not ("git_url" in lines[0] and "git_sha" in lines[1] and
                "image_tag" in lines[2]):
            logger.warning("Given repo {} not found via saasherder".format(
                repository))
            return None

        # def f(x): return {x.split("=")[0], x.split("=")[-1]}
        f = lambda x: {x.split("=")[0].strip(), x.split("=")[-1].strip()}
        values = {}
        [values.update(f(x)) for x in lines]
        return values
