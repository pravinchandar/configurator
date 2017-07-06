"""
This module actions the 'package' resource type specified in the
configuratior YAML file.
"""

import platform
from configurator.utils.logger import setup_logging

logger = setup_logging(logger_name=__name__, level='DEBUG')

class PackageManagerException(Exception):
    """
    All exceptions raised in PackageManager module are expected to be categorised
    as PackageManagerException
    """
    def __init__(self, message):
        self.message = message
        super(PackageManagerException, self).__init__(message)

class PackageManager(object):
    """
    This module provides a layer of abstraction to managing packages using
    APT package manager. As a consumer of this module, the user is expected
    to do the following.

    To install a package:

    >>> pack_man = PackageManager(package='tree')
    >>> pack_man.install()

    To uninstall a package:

    >>> pack_man = PackageManager(package='tree')
    >>> pack_man.uninstall()
    """
    def __init__(self, package):
        self.package = package
        #XXX Configurator only supports APT for now.
        self.package_provider = AptProvider(self.package)

    def __hash__(self):
        return hash(self.package)

    def install(self):
        self.package_provider.install()

    def uninstall(self):
        self.package_provider.uninstall()


class AptProvider(object):
    """
    This class provides APT specific functionalities. The functionalities
    are powered by the Python APT library.
    """
    def __init__(self, package):
        self.package = package
        self.cache = None

    def _update_cache(self):
        import apt
        self.cache = apt.cache.Cache()
        self.cache.update()

    def install(self):
        logger.debug("Preparing to install package '%s'...", self.package)
        self._update_cache()
        try:
            package = self.cache[self.package]
        except KeyError:
            msg = "Unable to find package '%s' in cache, skipping installation" % self.package
            return logger.error(msg)

        if package.is_installed:
            return logger.debug("Package '%s' is already installed", self.package)

        package.mark_install()

        try:
            logger.debug("Installing package '%s'...", self.package)
            self.cache.commit()
            logger.info("Installation of package '%s' is complete", self.package)
        except Exception as exc:
            logger.error("Package '%s' cannot be installed: %s", self.package, exc)

    def uninstall(self, purge=True):
        logger.debug("Preparing to uninstall package '%s'...", self.package)
        self._update_cache()
        package = self.cache[self.package]
        if not package:
            return logger.info("Package '%s' is not installed", self.package)
        package.mark_delete(purge=purge)
        try:
            logger.debug("Uninstalling package '%s'...", self.package)
            self.cache.commit()
            logger.info("Uninstalliation of package '%s' is complete", self.package)
        except Exception as exc:
            e_msg = "Package '%s' cannot be uninstalled: %s" % (self.package, exc)
            logger.error(e_msg)


class PackageResource(object):
    """
    This class models the 'resource' type found in the YAML file.

    The following actions on a package are supported:
        1. install
        2. uninstall
    """
    def __init__(self):
        self._to_install = set()
        self._to_uninstall = set()

    @property
    def supported_actions(self):
        return ['install', 'uninstall']

    @property
    def install(self):
        return self._to_install

    @install.setter
    def install(self, packages):
        for package in packages:
            self._to_install.add(PackageManager(package))

    @property
    def uninstall(self):
        return self._to_uninstall

    @uninstall.setter
    def uninstall(self, packages):
        for package in packages:
            self._to_uninstall.add(PackageManager(package))


def apply_package_resource(pkg_dict):
    """
    Provides the package resource interface.

    Usage:
        p = {'install': ['apache2', 'php5'], 'uninstall': ['tree']}
        apply_package_resource(p)
    """
    logger.info('Configuring packages based on the specified config...')
    pkg = PackageResource()
    for action, items in pkg_dict.iteritems():
        if action not in pkg.supported_actions:
            continue
        setattr(pkg, action, items)
    map(lambda x: x.install(), pkg.install)
    map(lambda x: x.uninstall(), pkg.uninstall)
