#!/usr/bin/env python3
import json
import logging
import sys
import os
import feedparser
import requests
import signal
import time
from f8a_worker.setup_celery import init_celery, init_selinon
from selinon import run_flow

from defaults import NPM_URL, PYPI_URL, ENABLE_SCHEDULING, \
    SCHEDULED_NPM_PACKAGES, SCHEDULED_PYPI_PACKAGES, PROBE_FILE_LOCATION


def run_liveness():
    # Remove all temp files to ensure that there are no leftovers
    if os.path.isfile(PROBE_FILE_LOCATION):
        os.remove(PROBE_FILE_LOCATION)

    for pid in psutil.process_iter():
        if pid.pid == 1:
            pid.send_signal(signal.SIGUSR1)
            time.sleep(10)

    sys.exit(0 if os.path.isfile(PROBE_FILE_LOCATION) else 1)


def write_package_info_to_file(node_args, file_path):
    with open(file_path, "a+") as f:
        f.write(node_args)
    return True


def get_correct_ecosystem_filepath(ecosystem):
    if ecosystem == 'npm':
        return SCHEDULED_NPM_PACKAGES
    if ecosystem == 'pypi':
        return SCHEDULED_PYPI_PACKAGES


def was_package_processed(ecosystem, name, version):
    ecosystem_file = get_correct_ecosystem_filepath(ecosystem)
    with open(ecosystem_file, "r") as f:
        print(f.readlines())
    return False


class ReleaseMnitor():
    """Class which check rss feeds for new releases"""

    def __init__(self):
        self.log = logging.getLogger(__name__)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logging_handler = logging.StreamHandler(sys.stdout)
        logging_handler.setFormatter(formatter)
        self.log.addHandler(logging_handler)
        self.log.level = logging.DEBUG

        if ENABLE_SCHEDULING:
            init_celery(result_backend=False)
            init_selinon()

    def run_package_analisys(self, name, ecosystem, version):
        """Run Selinon flow for analyses.
         :param name: name of the package to analyse
         :param version: package version
         :param ecosystem: package ecosystem
         :return: dispatcher ID serving flow
         """

        node_args = {
            'ecosystem': ecosystem,
            'name': name,
            'version': version,
            'recursive_limit': 0
        }

        write_package_info_to_file(node_args, get_correct_ecosystem_filepath(ecosystem))
        self.log.info("Scheduling Selinon flow '%s' with node_args: '%s'", 'bayesianFlow', node_args)
        return run_flow('bayesianFlow', node_args)

    def run(self):
        self.log.info("Initializing RSS feeds")
        feed_pypi = feedparser.parse(PYPI_URL + "rss/updates.xml")
        feed_npm = feedparser.parse(NPM_URL + "-/rss")

        while True:
            for i in feed_npm.entries:
                package_name = i['title']
                package_url = NPM_URL + "-/package/{package_name}/dist-tags".format(package_name=package_name)
                package_latest_version = json.loads(
                    requests.get(package_url, headers={'content-type': 'application/json'}).text).get('latest')
                self.log.info("Received event for npm: '%s':'%s'", package_name, package_latest_version)
                if ENABLE_SCHEDULING:
                    # self.run_package_analisys(package_name, 'npm', package_latest_version)
                    print({'package_name': package_name,
                           'latest_version': package_latest_version
                           })

            for i in feed_pypi.entries:
                package_name, package_latest_version = i['title'].split(' ')
                self.log.info("Received event for npm: '%s':'%s'", package_name, package_latest_version)
                if ENABLE_SCHEDULING:
                    # self.run_package_analisys(package_name, 'pypi', package_latest_version)
                    print({'package_name': package_name,
                           'latest_version': package_latest_version
                           })
