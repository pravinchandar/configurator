import os
import mock
from configurator.resources.command import apply_command_resource

def test_command_is_fired(mocker):
    """ The following tests if the command is fired correctly """
    c = {'rm -rf /tmp/cool_dir': None}
    mocked_subproc = mocker.patch('subprocess.check_call')
    apply_command_resource(c)
    mocked_subproc.assert_called_with(['rm', '-rf', '/tmp/cool_dir'])

def test_command_is_fired_only_when_a_condition_holds(mocker):
    """ The following tests if the command is fired correctly based on pre-condition"""
    c = {'rm -rf /tmp/cool_dir': {'onlyif': 'test -d /tmp/cool_dir'}}
    mocked_subproc = mocker.patch('subprocess.check_call')
    mocked_logger = mocker.patch('configurator.resources.command.logger.error')
    apply_command_resource(c)
    mocked_subproc.assert_called_with(['test', '-d', '/tmp/cool_dir'])
    s1 = "Requirement to execute '%s' wasn't satisfied"
    mocked_logger.assert_called_with(s1,'rm -rf /tmp/cool_dir' )

