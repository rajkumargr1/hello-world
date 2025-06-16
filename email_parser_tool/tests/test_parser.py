import unittest
import os
import logging
from email_parser_tool.parser import EmailParser
# InvalidEmailFormatException is not explicitly raised by parse_email_file for non-email files,
# it returns None. It's more for internal use or if a sub-parser raised it.
# from email_parser_tool.exceptions import InvalidEmailFormatException

# Helper to get the full path to a sample email
SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'sample_emails')

# Suppress most logging output during tests for cleaner test results
logging.basicConfig(level=logging.CRITICAL)
# If specific module logs are needed for debugging tests, set their level, e.g.:
# logging.getLogger('email_parser_tool.parser').setLevel(logging.DEBUG)


class TestEmailParser(unittest.TestCase):
    def setUp(self):
        self.parser = EmailParser()
        # Ensure sample files exist (basic check)
        self.assertTrue(os.path.exists(SAMPLES_DIR), f"Sample email directory not found: {SAMPLES_DIR}")
        self.assertTrue(os.path.exists(os.path.join(SAMPLES_DIR, 'plain_text_email.eml')), "plain_text_email.eml missing")

    def test_parse_plain_text_email(self):
        filepath = os.path.join(SAMPLES_DIR, 'plain_text_email.eml')
        data = self.parser.parse_email_file(filepath)
        self.assertIsNotNone(data, "Data should not be None for a valid email.")
        self.assertEqual(data['subject'], "Simple Test Email")
        self.assertEqual(data['from'], "sender@example.com")
        self.assertEqual(data['to'], "recipient@example.com")
        self.assertIn("This is the body of a simple plain text email.", data['body'])
        self.assertEqual(len(data['attachments']), 0)

    def test_parse_html_email(self):
        filepath = os.path.join(SAMPLES_DIR, 'html_email.eml')
        data = self.parser.parse_email_file(filepath)
        self.assertIsNotNone(data, "Data should not be None for a valid email.")
        self.assertEqual(data['subject'], "HTML Test Email")
        # The parser prioritizes plain text if available in multipart/alternative
        self.assertIn("This is the plain text part.", data['body'])
        self.assertEqual(len(data['attachments']), 0)

    def test_parse_email_with_attachment(self):
        filepath = os.path.join(SAMPLES_DIR, 'email_with_attachment.eml')
        data = self.parser.parse_email_file(filepath)
        self.assertIsNotNone(data, "Data should not be None for a valid email.")
        self.assertEqual(data['subject'], "Email with Attachment")
        self.assertIn("Please find the attached document.", data['body'])
        self.assertEqual(len(data['attachments']), 1)
        attachment = data['attachments'][0]
        self.assertEqual(attachment['filename'], "test_attachment.txt")
        self.assertEqual(attachment['content'], b"Hello, World!")

    def test_parse_email_with_multiple_attachments(self):
        filepath = os.path.join(SAMPLES_DIR, 'email_with_multiple_attachments.eml')
        data = self.parser.parse_email_file(filepath)
        self.assertIsNotNone(data, "Data should not be None for a valid email.")
        self.assertEqual(data['subject'], "Email with Multiple Attachments")
        self.assertEqual(len(data['attachments']), 2)

        # Order of attachments is not guaranteed, so check by filename
        attachments_by_filename = {att['filename']: att for att in data['attachments']}
        self.assertIn("file1.txt", attachments_by_filename)
        self.assertIn("file2.dat", attachments_by_filename)

        self.assertEqual(attachments_by_filename['file1.txt']['content'], b"File 1 Content")
        self.assertEqual(attachments_by_filename['file2.dat']['content'], b"File 2 Content")

    def test_parse_email_with_special_chars_subject(self):
        filepath = os.path.join(SAMPLES_DIR, 'email_with_special_chars_subject.eml')
        data = self.parser.parse_email_file(filepath)
        self.assertIsNotNone(data, "Data should not be None for a valid email.")
        self.assertEqual(data['subject'], 'Test! Subject with "Quotes" and <Special> Chars: &')

    def test_parse_no_subject_email(self):
        filepath = os.path.join(SAMPLES_DIR, 'no_subject_email.eml')
        data = self.parser.parse_email_file(filepath)
        self.assertIsNotNone(data, "Data should not be None for a valid email.")
        self.assertIsNone(data['subject'])

    def test_parse_empty_body_email(self):
        filepath = os.path.join(SAMPLES_DIR, 'empty_body_email.eml')
        data = self.parser.parse_email_file(filepath)
        self.assertIsNotNone(data, "Data should not be None for a valid email.")
        self.assertEqual(data['subject'], "Empty Body Test")
        self.assertEqual(data['body'].strip(), "")

    def test_parse_non_email_file(self):
        filepath = os.path.join(SAMPLES_DIR, 'not_an_email.txt')
        # Parser's general exception catch returns None
        data = self.parser.parse_email_file(filepath)
        self.assertIsNone(data, "Parsing a non-email file should return None.")

    def test_parse_non_existent_file(self):
        filepath = os.path.join(SAMPLES_DIR, 'non_existent_file.eml')
        # parse_email_file itself handles FileNotFoundError and returns None.
        # It also logs an error, which is good.
        # If we wanted to test that it *could* raise FileNotFoundError if not caught internally,
        # that would be a different kind of test, possibly on a helper method.
        # For the public method, returning None is the contract.
        data = self.parser.parse_email_file(filepath)
        self.assertIsNone(data, "Parsing a non-existent file should return None.")


    def test_parse_email_with_no_filename_attachment(self):
        filepath = os.path.join(SAMPLES_DIR, 'email_with_no_filename_attachment.eml')
        data = self.parser.parse_email_file(filepath)
        self.assertIsNotNone(data, "Data should not be None for a valid email.")
        self.assertEqual(data['subject'], "Email with No-Filename Attachment")
        self.assertEqual(len(data['attachments']), 1)
        attachment = data['attachments'][0]
        # The email.message.Message.get_filename() returns None if not found.
        self.assertIsNone(attachment['filename'])
        self.assertEqual(attachment['content'], b"NoNameAttachment")

if __name__ == '__main__':
    # This allows running the tests directly from this file:
    # python -m email_parser_tool.tests.test_parser
    # It's also common to run tests using `python -m unittest discover` or a test runner.
    logging.basicConfig(level=logging.INFO) # Enable logging for direct script run if desired
    logger = logging.getLogger('email_parser_tool.parser')
    logger.setLevel(logging.DEBUG) # Example: set parser logs to DEBUG for direct run
    unittest.main()
