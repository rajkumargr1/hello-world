import unittest
import collections

# Adjust import path based on how tests will be run.
from edi_eda.edi_eda.parser import parse_edi_message, get_delimiters
from edi_eda.edi_eda.analyzer import (
    count_transaction_sets,
    get_segment_frequency,
    extract_element_values,
    ParsedEDIData
)

# Re-using the sample from test_parser, focusing on the first transaction for simplicity in analyzer tests
# This sample includes an ISA with '~' as segment terminator and '>' as sub-element separator.
SAMPLE_EDI_FOR_ANALYZER = (
    "ISA*00*          *00*          *ZZ*SENDERID       *ZZ*RECEIVERID     *230101*1200*U*00401*000000001*0*P*>~"
    "GS*PO*SENDERID*RECEIVERID*20230101*1200*1*X*004010~"
    "ST*850*0001~"
    "BEG*00*SA*PURCHASEORDER123***20230101~"  # BEG03 is PO number, BEG04 is empty
    "N1*ST*RETAILER NAME*92*123456789~"
    "DTM*002*20230105~" # DTM02 is a date
    "PO1*1*10*EA*12.34**SK*SKU123~" # PO107 is SKU123
    "SE*5*0001~" # Number of segments from ST to SE is 5 (ST, BEG, N1, DTM, PO1)
    "GE*1*1~"
    "IEA*1*000000001~"
)

SAMPLE_EDI_WITH_SUB_ELEMENTS = (
    "ISA*00*          *00*          *ZZ*SENDERID       *ZZ*RECEIVERID     *230101*1200*U*00401*000000001*0*P*>~"
    "GS*PO*SENDERID*RECEIVERID*20230101*1200*1*X*004010~"
    "ST*850*0001~"
    "REF*ZZ*VALUE1>SUB1>SUB2*VALUE2~" # REF02 has sub-elements separated by '>'
    "SE*2*0001~"
    "GE*1*1~"
    "IEA*1*000000001~"
)


class TestAnalyzer(unittest.TestCase):

    def setUp(self):
        # Parse the main sample EDI content for most tests
        self.segment_terminator, self.element_separator, self.sub_element_separator = get_delimiters(SAMPLE_EDI_FOR_ANALYZER)
        self.parsed_edi_data: ParsedEDIData = parse_edi_message(
            SAMPLE_EDI_FOR_ANALYZER,
            self.segment_terminator,
            self.element_separator
        )

        # Parse the sample with sub-elements for specific tests
        self.seg_term_sub, self.el_sep_sub, self.sub_el_sep_sub = get_delimiters(SAMPLE_EDI_WITH_SUB_ELEMENTS)
        self.parsed_edi_with_sub_elements: ParsedEDIData = parse_edi_message(
            SAMPLE_EDI_WITH_SUB_ELEMENTS,
            self.seg_term_sub,
            self.el_sep_sub
        )


    def test_count_transaction_sets(self):
        counts = count_transaction_sets(self.parsed_edi_data)
        self.assertIsInstance(counts, collections.Counter)
        self.assertEqual(counts['850'], 1)
        self.assertEqual(len(counts), 1)

        # Test with empty data
        empty_counts = count_transaction_sets([])
        self.assertEqual(len(empty_counts), 0)

    def test_get_segment_frequency(self):
        frequency = get_segment_frequency(self.parsed_edi_data)
        self.assertIsInstance(frequency, collections.Counter)
        self.assertEqual(frequency['ISA'], 1)
        self.assertEqual(frequency['GS'], 1)
        self.assertEqual(frequency['ST'], 1)
        self.assertEqual(frequency['BEG'], 1)
        self.assertEqual(frequency['N1'], 1)
        self.assertEqual(frequency['DTM'], 1)
        self.assertEqual(frequency['PO1'], 1)
        self.assertEqual(frequency['SE'], 1)
        self.assertEqual(frequency['GE'], 1)
        self.assertEqual(frequency['IEA'], 1)
        self.assertEqual(len(frequency), 10)

        # Test with empty data
        empty_freq = get_segment_frequency([])
        self.assertEqual(len(empty_freq), 0)

        # Test with one segment that is empty list (e.g. from "~~" in parser)
        one_empty_segment_freq = get_segment_frequency([[]])
        self.assertEqual(len(one_empty_segment_freq), 0)

        # Test with one segment that has an empty string as ID (should not happen with good data)
        one_segment_empty_id_freq = get_segment_frequency([["", "data"]])
        self.assertEqual(one_segment_empty_id_freq[""], 1)


    def test_extract_element_values_existing(self):
        # BEG03 -> PURCHASEORDER123
        values = extract_element_values(self.parsed_edi_data, "BEG", 3)
        self.assertEqual(values, ["PURCHASEORDER123"])

        # DTM02 -> 20230105
        values_dtm = extract_element_values(self.parsed_edi_data, "DTM", 2)
        self.assertEqual(values_dtm, ["20230105"])

        # PO107 -> SKU123
        values_po1 = extract_element_values(self.parsed_edi_data, "PO1", 7)
        self.assertEqual(values_po1, ["SKU123"])

    def test_extract_element_values_missing_element(self):
        # BEG segment has 6 elements (index 0 to 5), so BEG07 (index 6) is out of bounds
        values = extract_element_values(self.parsed_edi_data, "BEG", 7) # 7th element
        self.assertEqual(values, [None]) # BEG segment exists, but element index is out of bounds

    def test_extract_element_values_empty_element(self):
        # BEG04 is present but empty
        values = extract_element_values(self.parsed_edi_data, "BEG", 4)
        self.assertEqual(values, [""])

    def test_extract_element_values_segment_not_found(self):
        values = extract_element_values(self.parsed_edi_data, "XXX", 1) # Segment XXX does not exist
        self.assertEqual(values, [])

    def test_extract_element_values_invalid_index(self):
        values = extract_element_values(self.parsed_edi_data, "BEG", 0) # 0-based index is invalid
        self.assertEqual(values, [])
        values_neg = extract_element_values(self.parsed_edi_data, "BEG", -1)
        self.assertEqual(values_neg, [])

    def test_extract_element_values_sub_elements(self):
        # Using self.parsed_edi_with_sub_elements and its determined sub_element_separator

        # REF02 -> VALUE1>SUB1>SUB2
        values_ref02 = extract_element_values(
            self.parsed_edi_with_sub_elements,
            "REF",
            2 # Element index for REF02
        )
        self.assertEqual(values_ref02, ["VALUE1>SUB1>SUB2"])

        # REF02, sub-element 1 -> VALUE1
        sub_values_1 = extract_element_values(
            self.parsed_edi_with_sub_elements,
            "REF",
            2, # Element index
            sub_element_separator=self.sub_el_sep_sub, # Should be '>'
            sub_element_index=1
        )
        self.assertEqual(sub_values_1, ["VALUE1"])
        self.assertEqual(self.sub_el_sep_sub, ">") # Ensure correct separator was used

        # REF02, sub-element 3 -> SUB2
        sub_values_3 = extract_element_values(
            self.parsed_edi_with_sub_elements,
            "REF",
            2,
            sub_element_separator=self.sub_el_sep_sub,
            sub_element_index=3
        )
        self.assertEqual(sub_values_3, ["SUB2"])

    def test_extract_element_values_sub_elements_missing_separator(self):
        # Attempt to extract sub-element without providing separator
        values = extract_element_values(
            self.parsed_edi_with_sub_elements,
            "REF",
            2,
            sub_element_index=1
            # sub_element_separator intentionally omitted
        )
        # Expect None because separator is required but not given
        self.assertEqual(values, [None])


    def test_extract_element_values_sub_elements_index_out_of_bounds(self):
        # REF02, sub-element 4 (does not exist)
        sub_values_oob = extract_element_values(
            self.parsed_edi_with_sub_elements,
            "REF",
            2,
            sub_element_separator=self.sub_el_sep_sub,
            sub_element_index=4
        )
        self.assertEqual(sub_values_oob, [None])

    def test_extract_element_values_sub_elements_invalid_index(self):
        sub_values_invalid = extract_element_values(
            self.parsed_edi_with_sub_elements,
            "REF",
            2,
            sub_element_separator=self.sub_el_sep_sub,
            sub_element_index=0 # Invalid sub-element index
        )
        self.assertEqual(sub_values_invalid, [None])


if __name__ == '__main__':
    unittest.main()
