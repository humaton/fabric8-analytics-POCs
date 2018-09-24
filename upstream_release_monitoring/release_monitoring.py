#!/usr/bin/env python3
import json
import os
import requests
import feedparser
from selinon import run_flow
from f8a_worker.setup_celery import init_celery, init_selinon

NPM_URL = "https://registry.npmjs.org/"
PYPI_URL = "https://pypi.org/"

feed_pypi = feedparser.parse(PYPI_URL+"rss/updates.xml")
feed_npm = feedparser.parse(NPM_URL + "-/rss")

def highest_number_of_entries():
    number_of_entries_pypi = len(feed_pypi.entries)
    number_of_entries_npm = len(feed_npm.entries)
    if (number_of_entries_npm > number_of_entries_pypi):
        return number_of_entries_npm
    elif (number_of_entries_npm < number_of_entries_pypi):
        return number_of_entries_pypi
    else:
        return number_of_entries_npm


def schedule_package_analisys(self, name, ecosystem, version):
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

    self.log.info("Scheduling Selinon flow '%s' with node_args: '%s'", 'bayesianFlow', node_args)
    return run_flow('bayesianFlow', node_args)


while True:
    for i in feed_npm.entries:
        package_name = i['title']
        package_url = NPM_URL+"-/package/{package_name}/dist-tags".format(package_name=package_name)
        package_latest_version = json.loads(requests.get(package_url, headers={'content-type': 'application/json'}).text)
        print({'package_name': package_name,
               'latest_version': package_latest_version.get('latest')
               })

    for i in feed_pypi.entries:
        package_name, package_latest_version = i['title'].split(' ')
        package_url = PYPI_URL+"-/pypi/{package_name}/json".format(package_name=package_name)
        print({'package_name': package_name,
               'latest_version': package_latest_version
               })







