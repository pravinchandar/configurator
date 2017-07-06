import os
import mock
from configurator.resources.file import apply_file_resource

def test_apply_file_resource_content(mocker):
    """ The following tests if the string is being written to correctly """
    f = {'/tmp/index.php': {'content': "<?php echo '<p>Hello World</p>'; ?>"}}
    mocker.patch('configurator.resources.service.ServiceResource.restart', return_value=True)
    apply_file_resource(f)
    with open('/tmp/index.php','r') as f:
        assert f.read() == "<?php echo '<p>Hello World</p>'; ?>"

def test_apply_file_resource_signal_service(mocker):
    """ The following tests if the service is signalled for a restart after file update """
    f = {'/tmp/index.php': {'content': "foo", 'mode': '0755', 'restart': ['apache2']}}
    mocked_service_restart = mocker.patch('configurator.resources.file.ServiceResource.restart')
    apply_file_resource(f)
    mocked_service_restart.assert_called_once_with()
