import unittest
import os
import tempfile

# Adjust import path based on how tests will be run.
# If running with 'python -m unittest discover edi_eda/tests' from the root directory,
# 'edi_eda.edi_eda.parser' should work.
from edi_eda.edi_eda.parser import read_edi_file, get_delimiters, parse_edi_message

SAMPLE_EDI_CONTENT_X12 = (
    "ISA*00*          *00*          *ZZ*SENDERID       *ZZ*RECEIVERID     *230101*1200*U*00401*000000001*0*P*>~"
    "GS*PO*SENDERID*RECEIVERID*20230101*1200*1*X*004010~"
    "ST*850*0001~"
    "BEG*00*SA*PURCHASEORDER123***20230101~"  # BEG03 is PURCHASEORDER123, BEG04 is empty
    "N1*ST*RETAILER NAME*92*123456789~"
    "SE*3*0001~" # SE01 is 3 (number of segments ST to SE)
    "GE*1*1~"
    "IEA*1*000000001~"
    "ISA*01*          *00*          *ZZ*SENDERID2      *ZZ*RECEIVERID2    *230102*1300*U*00401*000000002*0*T*^~\n" # Using \n as seg terminator
    "GS*PO*SENDERID2*RECEIVERID2*20230102*1300*2*X*004010\n"
    "ST*850*0002\n"
    "SE*1*0002\n"
    "GE*1*2\n"
    "IEA*1*000000002\n"
)

# For testing default delimiters
SAMPLE_EDI_NO_ISA = (
    "GS*PO*SENDERID*RECEIVERID*20230101*1200*1*X*004010~"
    "ST*850*0001~"
    "SE*1*0001~"
    "GE*1*1~"
    "IEA*1*000000001~"
)

SAMPLE_EDI_SHORT_ISA = "ISA*00*short~"


class TestParser(unittest.TestCase):

    def setUp(self):
        # Create a temporary file for testing read_edi_file
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=".txt")
        self.temp_file.write(SAMPLE_EDI_CONTENT_X12)
        self.temp_file.close()
        self.temp_file_path = self.temp_file.name

    def tearDown(self):
        os.remove(self.temp_file_path)

    def test_read_edi_file_success(self):
        content = read_edi_file(self.temp_file_path)
        self.assertEqual(content, SAMPLE_EDI_CONTENT_X12)

    def test_read_edi_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            read_edi_file("non_existent_file.edi")

    def test_get_delimiters_from_isa(self):
        # Test with the first ISA in SAMPLE_EDI_CONTENT_X12
        edi_portion_with_tilde_terminator = SAMPLE_EDI_CONTENT_X12.split("IEA*1*000000001~")[0] + "IEA*1*000000001~"
        segment_terminator, element_separator, sub_element_separator = get_delimiters(edi_portion_with_tilde_terminator)
        self.assertEqual(segment_terminator, '~')
        self.assertEqual(element_separator, '*')
        self.assertEqual(sub_element_separator, '>')

        # Test with the second ISA in SAMPLE_EDI_CONTENT_X12 (using \n as segment terminator)
        edi_portion_with_newline_terminator = SAMPLE_EDI_CONTENT_X12.split("IEA*1*000000001~")[1].strip()
        segment_terminator_2, element_separator_2, sub_element_separator_2 = get_delimiters(edi_portion_with_newline_terminator)
        self.assertEqual(segment_terminator_2, '\n')
        self.assertEqual(element_separator_2, '*') # ISA03
        self.assertEqual(sub_element_separator_2, '^') # ISA16

    def test_get_delimiters_default(self):
        # Test with content missing ISA
        segment_terminator, element_separator, sub_element_separator = get_delimiters(SAMPLE_EDI_NO_ISA)
        self.assertEqual(segment_terminator, '~') # Default
        self.assertEqual(element_separator, '*') # Default (or inferred)
        self.assertEqual(sub_element_separator, ':') # Default

        # Test with short ISA
        segment_terminator_short, element_separator_short, sub_element_separator_short = get_delimiters(SAMPLE_EDI_SHORT_ISA)
        self.assertEqual(segment_terminator_short, '~') # Default
        self.assertEqual(element_separator_short, '*') # Default
        self.assertEqual(sub_element_separator_short, ':') # Default

    def test_get_delimiters_empty_content(self):
        segment_terminator, element_separator, sub_element_separator = get_delimiters("")
        self.assertEqual(segment_terminator, '~')
        self.assertEqual(element_separator, '*')
        self.assertEqual(sub_element_separator, ':')


    def test_parse_edi_message_x12_tilde_terminator(self):
        # Using the first part of the sample content with '~'
        edi_to_parse = SAMPLE_EDI_CONTENT_X12.split("IEA*1*000000001~")[0] + "IEA*1*000000001~"
        # Deliberately provide the correct delimiters for this part
        parsed_data = parse_edi_message(edi_to_parse, segment_terminator='~', element_separator='*')

        self.assertEqual(len(parsed_data), 8) # ISA, GS, ST, BEG, N1, SE, GE, IEA
        self.assertEqual(parsed_data[0][0], "ISA")
        self.assertEqual(parsed_data[0][6], "SENDERID       ") # ISA06
        self.assertEqual(parsed_data[2][0], "ST")
        self.assertEqual(parsed_data[2][1], "850") # ST01
        self.assertEqual(parsed_data[2][2], "0001") # ST02
        self.assertEqual(parsed_data[3][1], "00")   # BEG01
        self.assertEqual(parsed_data[3][2], "SA")   # BEG02
        self.assertEqual(parsed_data[3][3], "PURCHASEORDER123") # BEG03
        self.assertEqual(parsed_data[3][4], "")     # BEG04 (empty element)
        self.assertEqual(parsed_data[3][5], "20230101") # BEG05
        self.assertEqual(parsed_data[5][1], "3") # SE01
        self.assertEqual(parsed_data[7][2], "000000001") # IEA02

    def test_parse_edi_message_x12_newline_terminator(self):
        # Using the second part of the sample content with '\n'
        edi_to_parse = SAMPLE_EDI_CONTENT_X12.split("IEA*1*000000001~")[1].strip()
         # Deliberately provide the correct delimiters for this part
        parsed_data = parse_edi_message(edi_to_parse, segment_terminator='\n', element_separator='*')

        self.assertEqual(len(parsed_data), 6) # ISA, GS, ST, SE, GE, IEA
        self.assertEqual(parsed_data[0][0], "ISA")
        self.assertEqual(parsed_data[0][6], "SENDERID2      ")
        self.assertEqual(parsed_data[2][0], "ST")
        self.assertEqual(parsed_data[2][1], "850")
        self.assertEqual(parsed_data[2][2], "0002")

    def test_parse_edi_message_empty_string(self):
        parsed_data = parse_edi_message("", segment_terminator='~', element_separator='*')
        self.assertEqual(len(parsed_data), 0)

    def test_parse_edi_message_only_delimiters(self):
        # Test with content that is just delimiters, or has empty segments
        parsed_data = parse_edi_message("~~", segment_terminator='~', element_separator='*')
        # This should result in two empty segments if we consider the content between terminators,
        # or one empty segment if the content is `~` (one segment, no elements).
        # Current implementation of split will give ['','',''] then pop will make it ['', '']
        # Each of these will be an empty list in parsed_segments
        self.assertEqual(len(parsed_data), 2)
        self.assertEqual(parsed_data[0], [])
        self.assertEqual(parsed_data[1], [])

        parsed_data_single_term = parse_edi_message("~", segment_terminator='~', element_separator='*')
        self.assertEqual(len(parsed_data_single_term), 1)
        self.assertEqual(parsed_data_single_term[0], [])


if __name__ == '__main__':
    unittest.main()
