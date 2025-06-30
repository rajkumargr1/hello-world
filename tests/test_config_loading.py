import unittest
import os
import yaml
from src.email_processor import load_config # Assuming load_config is in email_processor

# Define the path to the test configuration files within the tests directory
BASE_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
VALID_CONFIG_PATH = os.path.join(BASE_TEST_DIR, 'test_config_valid.yaml')
INVALID_CONFIG_PATH = os.path.join(BASE_TEST_DIR, 'test_config_invalid_syntax.yaml')
EMPTY_CONFIG_PATH = os.path.join(BASE_TEST_DIR, 'test_config_empty.yaml')
MINIMAL_CONFIG_PATH = os.path.join(BASE_TEST_DIR, 'test_config_minimal.yaml') # Missing required sections
NON_EXISTENT_CONFIG_PATH = os.path.join(BASE_TEST_DIR, 'non_existent_config.yaml')

# Sample valid config content
VALID_CONFIG_CONTENT = {
    "email_server": {
        "host": "imap.example.com",
        "port": 993,
        "user": "test@example.com",
        "password_env_var": "TEST_EMAIL_PASS"
    },
    "llm": {
        "api_key_env_var": "TEST_LLM_KEY",
        "model": "gemini-test"
    },
    "processing": {
        "output_csv_file": "data/test_output.csv",
        "temp_attachment_dir": "data/test_temp_attachments",
        "standard_template_senders": ["test_sender@example.com"]
    },
    "logging": {
        "level": "DEBUG"
    }
}

# Sample minimal config (missing required 'processing' section)
MINIMAL_CONFIG_CONTENT = {
    "email_server": {
        "host": "imap.example.com"
    }
    # Missing "processing" which is checked in load_config
}


class TestConfigLoading(unittest.TestCase):

    def setUp(self):
        """Create dummy config files for testing."""
        with open(VALID_CONFIG_PATH, 'w') as f:
            yaml.dump(VALID_CONFIG_CONTENT, f)

        with open(INVALID_CONFIG_PATH, 'w') as f:
            f.write("email_server: {host: 'imap.example.com', port: 993\nuser: 'test@example.com'") # Invalid YAML

        with open(EMPTY_CONFIG_PATH, 'w') as f:
            pass # Creates an empty file

        with open(MINIMAL_CONFIG_PATH, 'w') as f:
            yaml.dump(MINIMAL_CONFIG_CONTENT, f)


    def tearDown(self):
        """Remove dummy config files after tests."""
        os.remove(VALID_CONFIG_PATH)
        os.remove(INVALID_CONFIG_PATH)
        os.remove(EMPTY_CONFIG_PATH)
        os.remove(MINIMAL_CONFIG_PATH)
        if os.path.exists(NON_EXISTENT_CONFIG_PATH): # Should not be created by tests
             os.remove(NON_EXISTENT_CONFIG_PATH)


    def test_load_valid_config(self):
        """Test loading a correctly formatted and complete YAML config file."""
        config = load_config(VALID_CONFIG_PATH)
        self.assertIsNotNone(config)
        self.assertEqual(config['email_server']['host'], 'imap.example.com')
        self.assertEqual(config['llm']['model'], 'gemini-test')
        self.assertIn('test_sender@example.com', config['processing']['standard_template_senders'])
        self.assertEqual(config['logging']['level'], 'DEBUG')

    def test_load_non_existent_config(self):
        """Test loading a non-existent config file."""
        with self.assertRaises(FileNotFoundError):
            load_config(NON_EXISTENT_CONFIG_PATH)

    def test_load_invalid_yaml_config(self):
        """Test loading a config file with invalid YAML syntax."""
        with self.assertRaises(yaml.YAMLError):
            load_config(INVALID_CONFIG_PATH)

    def test_load_empty_config_file(self):
        """Test loading an empty config file."""
        # load_config raises ValueError if config is None (empty file results in None from yaml.safe_load)
        with self.assertRaises(ValueError) as context:
            load_config(EMPTY_CONFIG_PATH)
        self.assertIn("Config file is empty or invalid", str(context.exception))


    def test_load_config_missing_required_sections(self):
        """Test loading a config file that's valid YAML but missing required sections."""
        with self.assertRaises(ValueError) as context:
            load_config(MINIMAL_CONFIG_PATH)
        # The error message in load_config checks for 'email_server' or 'processing'
        self.assertTrue("Config file missing required sections" in str(context.exception))
        self.assertTrue("'processing'" in str(context.exception)) # Specifically processing is missing here


if __name__ == '__main__':
    # This allows running the tests directly from this file
    # For project-wide testing, use 'python -m unittest discover tests' from the root directory
    unittest.main()
