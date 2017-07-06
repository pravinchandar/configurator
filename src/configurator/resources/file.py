"""
This module actions the 'file' resource type specified in the
configurator YAML file.
"""
import os
import pwd
import grp
import hashlib
import shutil
import stat

from configurator.utils.logger import setup_logging
from configurator.resources.service import ServiceResource

logger = setup_logging(logger_name=__name__, level='INFO')

class FileResource(object):
    """
    This class models the 'file' resource type found in the configurator
    YAML file.

    Following actions are supported on a file:
        1. Ability to write a string to the taget file
        2. Ability to copy contents from a specified file to the target file.
        3. Ability to update metadata on the target file (user, root and mode)
        4. Ability to refresh services after a successful update to the target file.

    Note: The actions performed on a file are idempotent.
    """
    def __init__(self, file_name):
        self._target_file = file_name
        self._refreshed = False
        self._services_to_restart = set()

    @property
    def supported_metadata(self):
        return ['owner', 'group', 'mode', 'content', 'clone', 'restart']

    @property
    def refreshed(self):
        return self._refreshed

    @refreshed.setter
    def refreshed(self, value=True):
        """ Record if the file was updated """
        self._refreshed = True

    @property
    def restart(self):
        return self._services_to_restart

    @restart.setter
    def restart(self, services):
        for service in services:
            self._services_to_restart.add(ServiceResource(service))

    @property
    def mode(self):
        if os.path.exists(self._target_file):
            return oct(stat.S_IMODE(os.lstat(self._target_file).st_mode))

    @mode.setter
    def mode(self, value='0600'):
        if int(self.mode, 8) != int(value, 8):
            from_m  = self.mode
            to_m = oct(int(value, 8))
            logger.info("Changing %s mode from: %s to: %s", self._target_file, from_m, to_m)
            os.chmod(self._target_file, int(value, 8))

    @property
    def owner(self):
        if os.path.exists(self._target_file):
            return pwd.getpwuid(os.stat(self._target_file).st_uid).pw_name

    @owner.setter
    def owner(self, value='root'):
        if os.path.exists(self._target_file):
            os.chown(self._target_file, pwd.getpwnam(value).pw_uid, -1)

    @property
    def group(self):
        if os.path.exists(self._target_file):
            return grp.getgrgid(os.stat(self._target_file).st_gid)[0]

    @group.setter
    def group(self, value='root'):
        if os.path.exists(self._target_file):
            os.chown(self._target_file, -1, grp.getgrnam(value).gr_gid)

    @staticmethod
    def compute_md5(target, string=False):
        try:
            if string:
                return hashlib.md5(target).hexdigest()
            else:
                return hashlib.md5(open(target, 'rb').read()).hexdigest()
        except IOError:
            pass

    @property
    def md5(self):
        return self.compute_md5(self._target_file)

    @property
    def content(self):
        return

    @content.setter
    def content(self, content_string):
        logger.debug("Preparing to update contents of %s...", self._target_file)
        if self.md5 == self.compute_md5(content_string, string=True):
            logger.debug("Contents update to %s not required", self._target_file)
            return
        with open(self._target_file, 'w') as f:
            f.write(content_string)
            self.refreshed = True
        logger.info("Updated contents of %s", self._target_file)

    @property
    def clone(self):
        return

    @clone.setter
    def clone(self, src):
        logger.debug("Preparing to clone %s to %s...", src, self._target_file)
        if not os.path.exists(src):
            return logger.error("The file %s doesn't exist, please check your config", src)
        if self.md5 == self.compute_md5(src):
            msg = "The md5sum of %s and %s match, no action required" % (src, self._target_file)
            return logger.debug(msg)

        shutil.copyfile(src, self._target_file)
        self.refreshed = True
        logger.info("Contents of %s are copied to %s", src, self._target_file)


def apply_file_resource(file_dict):
    """
    Provides the file resource interface.

    Example usage:
        The following example writes to the file /var/www/index.php with
        the specified content and permissions. It also refreshes the apache2
        service after a successful update to the PHP file.

        f = {'/var/www/index.php': {'content': "<?php echo '<p>Hello World</p>'; ?>", 'mode': '0755', 'restart': ['apache2']}
        appl_file_resource(f)

    """
    logger.info('Configuring files based on the specified config...')
    for name, metadata in file_dict.iteritems():
        f = FileResource(name)
        filtered = {k: v for k, v in metadata.items() if k in f.supported_metadata}
        for meta, value in filtered.iteritems():
            setattr(f, meta, value)
        if f.refreshed:
            map(lambda x: x.restart(), f.restart)

