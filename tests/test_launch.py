"""Tests for VS Code launch configurations."""
import json
import os
from pathlib import Path
import pytest

@pytest.fixture
def launch_config():
    """Load launch.json configuration."""
    launch_path = Path(__file__).parent.parent / '.vscode' / 'launch.json'
    with open(launch_path) as f:
        return json.load(f)

def test_debug_tests_configuration(launch_config):
    """Test Python Debug Tests configuration."""
    debug_tests = next(
        config for config in launch_config['configurations'] 
        if config['name'] == 'Python: Debug Tests'
    )
    
    assert debug_tests['type'] == 'python'
    assert debug_tests['request'] == 'launch'
    assert debug_tests['program'].endswith('pytest')
    assert '-v' in debug_tests['args']
    assert '-s' in debug_tests['args']
    assert 'tests/test_camera.py' in debug_tests['args']
    assert debug_tests['console'] == 'integratedTerminal'
    assert debug_tests['justMyCode'] is False