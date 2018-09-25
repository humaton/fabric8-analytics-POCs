#!/usr/bin/env python3
import json
import logging

import feedparser
import requests
from f8a_worker.setup_celery import init_celery, init_selinon
from selinon import run_flow

from defaults import NPM_URL, PYPI_URL, ENABLE_SCHEDULING, \
    SCHEDULED_NPM_PACKAGES, SCHEDULED_PYPI_PACKAGES


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

    def write_package_info_to_file(self, node_args, file_path):
        with open(file_path, "a+") as f:
            f.write(node_args)
        return True

    def get_correct_ecosystem_filepath(self, ecosystem):
        if ecosystem == 'npm':
            return SCHEDULED_NPM_PACKAGES
        if ecosystem == 'pypi':
            return SCHEDULED_PYPI_PACKAGES

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

        self.write_package_info_to_file(node_args, self.get_correct_ecosystem_filepath(ecosystem))
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
                print({'package_name': package_name,
                       'latest_version': package_latest_version
                       })
                self.log.info("Received event for npm: '%s':'%s'", package_name, package_latest_version)
                if ENABLE_SCHEDULING:
                    self.run_package_analisys(package_name, 'npm', package_latest_version)

            for i in feed_pypi.entries:
                package_name, package_latest_version = i['title'].split(' ')
                print({'package_name': package_name,
                       'latest_version': package_latest_version
                       })
                self.log.info("Received event for npm: '%s':'%s'", package_name, package_latest_version)
                if ENABLE_SCHEDULING:
                    self.run_package_analisys(package_name, 'pypi', package_latest_version)
