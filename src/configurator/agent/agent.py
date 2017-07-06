import yaml
import socket
import sys
import os.path

from configurator.utils.logger import setup_logging

from configurator.resources.file import apply_file_resource
from configurator.resources.service import apply_service_resource
from configurator.resources.command import apply_command_resource
from configurator.resources.package import apply_package_resource

logger = setup_logging(logger_name=__name__, level='DEBUG')

with open("configurator.yaml", 'r') as stream:
    try:
        config = yaml.load(stream)
        hosts = filter(lambda x: socket.gethostname() == x, config.keys())
        if len(hosts) == 0:
           logger.error("Cannot find config to apply for '%s'", socket.gethostname())
           sys.exit(0)
    except yaml.YAMLError as exc:
        logger.error(exc)
        sys.exit(1)

logger.info("Applying config for '%s'", hosts[0])

for host, resource in config.iteritems():
    if 'package' in resource.keys():
        apply_package_resource(config[host]['package'])
    if 'file' in resource.keys():
        apply_file_resource(config[host]['file'])
    if 'command' in resource.keys():
        apply_command_resource(config[host]['command'])
