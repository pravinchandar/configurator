"""
This module actions the 'command' resource type specified in the
configurator YAML file.
"""
import shlex
import subprocess

from configurator.utils.logger import setup_logging
from configurator.resources.service import ServiceResource

logger = setup_logging(logger_name=__name__, level='INFO')

class CommandResource(object):
    """
    This class models the 'command' resource type found in the configurator
    YAML file.

    Following actions are supported per command:
        1. Ability to restart services based on a successful run of the command.
        4. Ability to run the command on a condition.
    """
    def __init__(self, command):
        self.command = command
        self.exit_code = None
        self._only_if = None
        self._services_to_restart = set()

    @property
    def supported_actions(self):
        """
        The following actions are supported per command
            1. restart: Restart a service after a successful run.
            2. onlyif: Run the command only if a condition command's $? is 0.
        """
        return ['restart', 'onlyif']

    def run(self):
        logger.debug("Executing '%s'", self.command)
        if self.onlyif:
            logger.debug("Executing the requirement '%s'", self.onlyif)
            if self.execute(self.onlyif) == 0:
                self.exit_code = self.execute(self.command)
            else:
                logger.error("Requirement to execute '%s' wasn't satisfied", self.command)
        else:
            self.exit_code = self.execute(self.command)

    @property
    def restart(self):
        return self._services_to_restart

    @restart.setter
    def restart(self, services):
        for service in services:
            self._services_to_restart.add(ServiceResource(service))

    @property
    def onlyif(self):
        return self._only_if

    @onlyif.setter
    def onlyif(self, value):
        self._only_if = value

    def execute(self, command):
        try:
            return subprocess.check_call(shlex.split(command))
        except subprocess.CalledProcessError as exc:
            return 1

def apply_command_resource(cmd):
    """
    Provides the command resource interface.

    Example usage:
        The following example will remove the directory /tmp/cool_dir
        based on the condition that it exists.

        c = {'rm -rf /tmp/cool_dir': {'onlyif': 'test -d /tmp/cool_dir'}}
        appl_command_resource(c)
    """

    logger.info('Executing commands based on the specified config...')
    for name, metadata in cmd.iteritems():
        command = CommandResource(name)
        if isinstance(metadata, dict):
            filtered = {k: v for k, v in metadata.items() if k in command.supported_actions}
            for meta, value in filtered.iteritems():
                setattr(command, meta, value)
        command.run()
        if command.exit_code == 0:
            map(lambda dep: dep.restart(), command.restart)
