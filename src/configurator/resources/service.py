import subprocess
from configurator.utils.logger import setup_logging

logger = setup_logging(logger_name=__name__, level='DEBUG')

class ServiceResource(object):
    def __init__(self, name):
        self.name = name

    def stop(self):
        logger.info("Stopping service %s...", self.name)
        subprocess.call(['service', self.name, 'stop'])
        logger.info("Stopped service %s", self.name)

    def start(self):
        logger.info("Starting service %s...", self.name)
        subprocess.call(['service', self.name, 'start'])
        logger.info("Started service %s", self.name)

    def reload(self):
        logger.info("Reloading service %s...", self.name)
        subprocess.call(['service', self.name, 'reload'])
        logger.info("Reloaded service %s", self.name)

    def restart(self):
        logger.info("Restarting service %s...", self.name)
        subprocess.call(['service', self.name, 'restart'])
        logger.info("Restarted service %s", self.name)

    def status(self):
        pass

def apply_service_resource(service_dict):
    for service, state in service_dict.iteritems():
        print state

def build_file_resource(file_dict):
    for name, metadata in file_dict.iteritems():
        f = FileResource(name)
        filtered = {k: v for k, v in metadata.items() if k in f.supported_metadata}
        for meta, value in filtered.iteritems():
            setattr(f, meta, value)
        if f.refreshed:
            map(lambda x: x.restart(), f.restart)

