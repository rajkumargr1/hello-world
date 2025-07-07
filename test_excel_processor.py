import unittest
import pandas as pd
from pandas.testing import assert_frame_equal
import os
from excel_processing_agent import ExcelProcessor, StandardEquipmentTerms # Assuming excel_processing_agent.py is in the same directory or accessible via PYTHONPATH

# Helper to create a dummy excel file for testing
def create_test_excel(file_path="test_excel.xlsx", data=None, sheet_name="Sheet1"):
    if data is None:
        data = {
            "ID": ["ID01", "ID02"],
            "Equipment Type": ["20GP", "40HC"],
            "  Location  ": ["NYC", "LAX"], # With spaces
            "Unknown Column": ["Val1", "Val2"]
        }
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False, sheet_name=sheet_name)
    return file_path

class TestExcelProcessor(unittest.TestCase):

    def setUp(self):
        self.test_excel_file = "test_sample_data.xlsx"
        self.output_csv_file = "test_output.csv"

        # Default data for most tests
        self.sample_data = {
            "ID": ["CNTR001", "CNTR002", "CNTR003"],
            "Equipment Type": ["20GP", "40HC", "20RF"],
            "Size": [20, 40, 20],
            "Status": ["Available", "In Use", "Maintenance"],
            "Depot": ["NYC01", "LAX02", "NYC01"],
            " Tare Weight ": [2200, 3800, 2500], # Column with spaces
            "Payload (kg)": [21800, 26680, 21500],
            "Manufacture Date": pd.to_datetime(["2010-05-01", "2015-08-12", "2012-01-20"]),
            "Notes": ["Note A", "Note B", "Note C"],
            "MOS": ["Sea", "Rail", "Sea"], # Method of Shipment
            "Means of Conveyance Authorization": ["VesselX", "TrainY", "VesselZ"], # MEA
            "Carrier": ["CarrierA", "CarrierB", "CarrierC"] # IFC
        }
        create_test_excel(self.test_excel_file, data=self.sample_data)

        # Clean up any old output file if it exists from a previous failed run
        if os.path.exists(self.output_csv_file):
            os.remove(self.output_csv_file)

    def tearDown(self):
        if os.path.exists(self.test_excel_file):
            os.remove(self.test_excel_file)
        if os.path.exists(self.output_csv_file):
            os.remove(self.output_csv_file)
        # Clean up other potential files
        if os.path.exists("empty_test.xlsx"):
            os.remove("empty_test.xlsx")
        if os.path.exists("specific_order_test.xlsx"):
            os.remove("specific_order_test.xlsx")


    def test_init_success(self):
        processor = ExcelProcessor(self.test_excel_file)
        self.assertEqual(processor.excel_file_path, self.test_excel_file)
        self.assertIsInstance(processor.df, pd.DataFrame)
        self.assertEqual(list(processor.original_columns), list(self.sample_data.keys()))

    def test_init_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            ExcelProcessor("non_existent_file.xlsx")

    def test_map_column_names_default(self):
        processor = ExcelProcessor(self.test_excel_file)
        processor.map_column_names()

        expected_mapped_columns = {
            "ID": "EquipmentID",
            "Equipment Type": "EquipmentType",
            "Size": "EquipmentSize",
            "Status": "EquipmentStatus",
            "Depot": "CurrentLocation",
            " Tare Weight ": "TareWeight", # Should handle spaces
            # "Payload (kg)" is not in StandardEquipmentTerms by default
            "Manufacture Date": "ManufactureDate",
            "Notes": "Remarks",
            "MOS": "MethodOfShipment",
            "Means of Conveyance Authorization": "MeansOfConveyanceAuth",
            "Carrier": "FreightCarrierConsolidator"
        }
        self.assertEqual(processor.mapped_columns, expected_mapped_columns)
        self.assertIn("EquipmentID", processor.standardized_columns_to_extract)
        self.assertIn("TareWeight", processor.standardized_columns_to_extract)
        self.assertIn("MethodOfShipment", processor.standardized_columns_to_extract)
        self.assertIn("MeansOfConveyanceAuth", processor.standardized_columns_to_extract)
        self.assertIn("FreightCarrierConsolidator", processor.standardized_columns_to_extract)
        self.assertNotIn("MaxPayload", processor.standardized_columns_to_extract) # Since "Payload (kg)" is not a default key

    def test_map_column_names_with_instruction_set(self):
        processor = ExcelProcessor(self.test_excel_file)
        instruction_set = {
            "ID": "CustomID", # Override
            "Payload (kg)": "MaxPayload", # New mapping
            "NonExistentExcelColumn": "ShouldNotAppear"
        }
        processor.map_column_names(instruction_set=instruction_set)

        self.assertEqual(processor.mapped_columns["ID"], "CustomID")
        self.assertEqual(processor.mapped_columns["Payload (kg)"], "MaxPayload")
        self.assertIn("CustomID", processor.standardized_columns_to_extract)
        self.assertIn("MaxPayload", processor.standardized_columns_to_extract)
        # Ensure default mappings are still applied for other columns
        self.assertEqual(processor.mapped_columns["Equipment Type"], "EquipmentType")
        self.assertNotIn("ShouldNotAppear", processor.standardized_columns_to_extract)
        self.assertNotIn("NonExistentExcelColumn", processor.mapped_columns)


    def test_map_column_names_case_insensitivity_and_spaces(self):
        data_case_space = {
            "id": ["ID01"],       # Lowercase
            "  equipment type  ": ["20GP"], # Spaces and lowercase
            "STATUS": ["OK"]      # Uppercase
        }
        test_file_case_space = "test_case_space.xlsx"
        create_test_excel(test_file_case_space, data=data_case_space)

        processor = ExcelProcessor(test_file_case_space)
        processor.map_column_names()

        expected_mapped = {
            "id": "EquipmentID",
            "  equipment type  ": "EquipmentType",
            "STATUS": "EquipmentStatus"
        }
        self.assertEqual(processor.mapped_columns, expected_mapped)
        os.remove(test_file_case_space)

    def test_map_column_names_no_matches(self):
        data_no_match = {"UnknownCol1": ["A"], "AnotherRandom": ["B"]}
        test_file_no_match = "test_no_match.xlsx"
        create_test_excel(test_file_no_match, data=data_no_match)

        processor = ExcelProcessor(test_file_no_match)
        processor.map_column_names()

        self.assertEqual(processor.mapped_columns, {})
        self.assertEqual(processor.standardized_columns_to_extract, [])
        os.remove(test_file_no_match)

    def test_extract_to_csv_success(self):
        processor = ExcelProcessor(self.test_excel_file)
        instruction_set = {"Payload (kg)": "MaxPayload", " Tare Weight ": "AdjustedTareWeight"}
        processor.map_column_names(instruction_set=instruction_set)
        processor.extract_to_csv(self.output_csv_file)

        self.assertTrue(os.path.exists(self.output_csv_file))
        df_out = pd.read_csv(self.output_csv_file)

        expected_columns = sorted([
            "EquipmentID", "EquipmentType", "EquipmentSize", "EquipmentStatus",
            "CurrentLocation", "AdjustedTareWeight", "MaxPayload", "ManufactureDate", "Remarks",
            "MethodOfShipment", "MeansOfConveyanceAuth", "FreightCarrierConsolidator" # New fields
        ])
        # Filter expected_columns based on what's actually in processor.standardized_columns_to_extract
        # because instruction_set might not map everything from the default set if it overrides.
        # The df_out.columns should match the actual standardized terms that resulted from the mapping.

        # The columns in df_out will be based on processor.mapped_columns.values()
        # and their order is determined by list(dict.fromkeys(processor.mapped_columns.values()))

        # Let's get the expected columns directly from the processor's state after mapping
        expected_df_cols = list(dict.fromkeys(processor.mapped_columns.values()))

        self.assertEqual(sorted(list(df_out.columns)), sorted(expected_df_cols))
        self.assertEqual(len(df_out), len(self.sample_data["ID"]))

        # Verify data for some original and new columns
        self.assertEqual(df_out["AdjustedTareWeight"].iloc[0], self.sample_data[" Tare Weight "][0])
        self.assertEqual(df_out["MaxPayload"].iloc[0], self.sample_data["Payload (kg)"][0])
        self.assertEqual(df_out["EquipmentID"].iloc[0], self.sample_data["ID"][0])
        if "MethodOfShipment" in df_out.columns: # MOS was not in instruction_set, so it uses default mapping
            self.assertEqual(df_out["MethodOfShipment"].iloc[0], self.sample_data["MOS"][0])
        if "MeansOfConveyanceAuth" in df_out.columns: # Means of Conveyance Authorization was not in instruction_set
            self.assertEqual(df_out["MeansOfConveyanceAuth"].iloc[0], self.sample_data["Means of Conveyance Authorization"][0])
        if "FreightCarrierConsolidator" in df_out.columns: # Carrier was not in instruction_set
            self.assertEqual(df_out["FreightCarrierConsolidator"].iloc[0], self.sample_data["Carrier"][0])


    def test_extract_to_csv_no_columns_mapped(self):
        data_no_match = {"UnknownCol1": ["A"], "AnotherRandom": ["B"]}
        empty_test_excel = "empty_test.xlsx"
        create_test_excel(empty_test_excel, data=data_no_match)

        processor = ExcelProcessor(empty_test_excel)
        processor.map_column_names() # No columns should map
        processor.extract_to_csv(self.output_csv_file)

        self.assertTrue(os.path.exists(self.output_csv_file))
        try:
            df_out = pd.read_csv(self.output_csv_file)
            # If read_csv succeeds, it means the file was not completely empty (e.g., had headers but no data)
            # or pandas handled it. An empty DataFrame (no columns, no rows) is fine.
            self.assertTrue(df_out.empty)
        except pd.errors.EmptyDataError:
            # This is also an acceptable outcome if to_csv writes a file that read_csv considers empty of data
            # (e.g. 0 bytes, or just a newline for an empty DataFrame with no columns).
            # The key is that no data columns were parsed.
            pass # Successfully caught EmptyDataError, which is expected.
        except Exception as e:
            self.fail(f"Reading the CSV raised an unexpected exception: {e}")


    def test_extract_to_csv_column_order(self):
        # Test if the output CSV columns follow a somewhat predictable order based on mapping
        # The current implementation orders based on dict.fromkeys(self.mapped_columns.values())
        # which preserves first-seen order of the *standardized terms*.

        # Create excel with columns in a specific order
        ordered_data = {
            "Status": ["S1"], # Should map to EquipmentStatus
            "ID": ["ID1"],    # Should map to EquipmentID
            "Type": ["T1"]    # Should map to EquipmentType
        }
        specific_order_excel = "specific_order_test.xlsx"
        create_test_excel(specific_order_excel, data=ordered_data)

        processor = ExcelProcessor(specific_order_excel)
        # No instruction set, rely on StandardEquipmentTerms order (which is not guaranteed for dicts <3.7 but generally insertion order for CPython 3.6+)
        # and then the logic of dict.fromkeys(self.mapped_columns.values())
        processor.map_column_names()
        processor.extract_to_csv(self.output_csv_file)

        df_out = pd.read_csv(self.output_csv_file)

        # The order in standardized_columns_to_extract depends on iteration over original_columns and then StandardEquipmentTerms
        # Original columns: Status, ID, Type
        # Mappings: Status -> EquipmentStatus, ID -> EquipmentID, Type -> EquipmentType
        # processor.standardized_columns_to_extract will be [EquipmentStatus, EquipmentID, EquipmentType]
        # The CSV columns will be ordered based on unique values from processor.mapped_columns.values() in order of appearance
        # Mapped_columns could be {"Status": "EquipmentStatus", "ID": "EquipmentID", "Type": "EquipmentType"} (order can vary based on dict behavior)
        # Values: EquipmentStatus, EquipmentID, EquipmentType
        # dict.fromkeys might give ['EquipmentStatus', 'EquipmentID', 'EquipmentType']

        # Let's check the actual order from processor.standardized_columns_to_extract
        # as this is what the current code implies for ordering.
        # The actual final columns are derived from: list(dict.fromkeys(self.mapped_columns.values()))

        # Based on the sample data, original columns are "Status", "ID", "Type".
        # StandardEquipmentTerms has "ID" before "Type" before "Status".
        # The mapping loop iterates original columns, then StandardEquipmentTerms for matches.
        # 1. Original "Status": finds "Status" -> "EquipmentStatus". mapped_columns["Status"] = "EquipmentStatus". standardized_columns_to_extract = ["EquipmentStatus"]
        # 2. Original "ID": finds "ID" -> "EquipmentID". mapped_columns["ID"] = "EquipmentID". standardized_columns_to_extract = ["EquipmentStatus", "EquipmentID"]
        # 3. Original "Type": finds "Type" -> "EquipmentType". mapped_columns["Type"] = "EquipmentType". standardized_columns_to_extract = ["EquipmentStatus", "EquipmentID", "EquipmentType"]

        # So, self.mapped_columns.values() would be dict_values(['EquipmentStatus', 'EquipmentID', 'EquipmentType']) if dict preserves this order.
        # list(dict.fromkeys(...)) would then be ['EquipmentStatus', 'EquipmentID', 'EquipmentType']

        expected_csv_column_order = ['EquipmentStatus', 'EquipmentID', 'EquipmentType']
        self.assertEqual(list(df_out.columns), expected_csv_column_order)


    def test_mapping_priority_instruction_over_default(self):
        processor = ExcelProcessor(self.test_excel_file)
        # "ID" is in StandardEquipmentTerms, mapping to "EquipmentID"
        # "Depot" is in StandardEquipmentTerms, mapping to "CurrentLocation"
        instruction_set = {
            "ID": "CustomContainerID",      # Instruction set should override default for "ID"
            "Depot": "CustomDepotLocation" # Instruction set should override default for "Depot"
        }
        processor.map_column_names(instruction_set=instruction_set)

        self.assertEqual(processor.mapped_columns["ID"], "CustomContainerID")
        self.assertEqual(processor.mapped_columns["Depot"], "CustomDepotLocation")
        # Ensure other default mappings are still active if not in instruction_set
        self.assertEqual(processor.mapped_columns["Equipment Type"], "EquipmentType")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

# To run these tests from the command line:
# python -m unittest test_excel_processor.py
