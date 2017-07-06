import os
import mock
from configurator.resources.package import *

def test_package_install_interface(mocker):
    """ The following tests if the packages for installation is following correct logic """
    p = {'install': ['apache2']}
    mocked_pacman = mocker.patch('configurator.resources.package.PackageManager')
    apply_package_resource(p)
    mocked_pacman.assert_called_with('apache2')
