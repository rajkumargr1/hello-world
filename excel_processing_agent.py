import pandas as pd

# Step 1: Define the StandardEquipmentTerms dictionary
StandardEquipmentTerms = {
    # Potential Excel Column Name Variations: Standardized Term
    "ID": "EquipmentID",
    "Equipment ID": "EquipmentID",
    "Container No.": "EquipmentID",
    "Container Number": "EquipmentID",
    "Serial No.": "EquipmentID",
    "Serial Number": "EquipmentID",

    "Type": "EquipmentType",
    "Equipment Type": "EquipmentType",
    "Container Type": "EquipmentType",
    "ISO Code": "EquipmentType", # Often ISO codes denote type + size

    "Size": "EquipmentSize",
    "Equipment Size": "EquipmentSize",
    "Length": "EquipmentSize", # Could be part of size

    "Status": "EquipmentStatus",
    "Equipment Status": "EquipmentStatus",
    "Availability": "EquipmentStatus",
    "Condition": "EquipmentStatus",

    "Location": "CurrentLocation",
    "Current Location": "CurrentLocation",
    "Depot": "CurrentLocation",
    "Port": "CurrentLocation",

    "Customer": "Customer",
    "Client": "Customer",
    "Assigned To": "Customer",

    "Last Movement Date": "LastMovementDate",
    "Date of Last Move": "LastMovementDate",
    "Last Activity": "LastMovementDate",

    "Maintenance Due": "MaintenanceDueDate",
    "Next Maintenance": "MaintenanceDueDate",
    "Inspection Date": "MaintenanceDueDate",

    "Tare Weight": "TareWeight",
    "Weight (Tare)": "TareWeight",

    "Max Payload": "MaxPayload",
    "Maximum Payload": "MaxPayload",
    "Payload Capacity": "MaxPayload",

    "Max Gross Weight": "MaxGrossWeight",
    "Maximum Gross Weight": "MaxGrossWeight",

    "Manufacture Date": "ManufactureDate",
    "Build Date": "ManufactureDate",
    "Year of Manufacture": "ManufactureDate",

    "Notes": "Remarks",
    "Comments": "Remarks",
    "Additional Info": "Remarks",

    # Movement Related Terms
    "MOS": "MethodOfShipment",
    "Method of Shipment": "MethodOfShipment",
    "Shipment Method": "MethodOfShipment",

    "MEA": "MeansOfConveyanceAuth",
    "Means of Conveyance Authorization": "MeansOfConveyanceAuth",
    "Conveyance Auth": "MeansOfConveyanceAuth",

    "IFC": "FreightCarrierConsolidator",
    "Inland Freight Carrier": "FreightCarrierConsolidator",
    "International Freight Consolidator": "FreightCarrierConsolidator",
    "Carrier": "FreightCarrierConsolidator", # Generic, might overlap, be cautious
    "Freight Forwarder": "FreightCarrierConsolidator",


    # Add more mappings as needed based on common variations
}


class ExcelProcessor:
    """
    Processes an Excel file to extract and standardize shipping equipment data.
    """
    def __init__(self, excel_file_path):
        """
        Initializes the ExcelProcessor with the path to the Excel file.

        Args:
            excel_file_path (str): The path to the .xlsx or .xls file.

        Raises:
            FileNotFoundError: If the Excel file does not exist.
            Exception: If there's an error reading the Excel file.
        """
        try:
            self.excel_file_path = excel_file_path
            self.df = pd.read_excel(excel_file_path)
            self.original_columns = list(self.df.columns)
            self.mapped_columns = {} # To store original_col: standard_col
            self.standardized_columns_to_extract = [] # List of standard terms that were found/mapped
            print(f"Successfully loaded Excel file: {excel_file_path}")
            print(f"Original columns identified: {self.original_columns}")
        except FileNotFoundError:
            print(f"Error: Excel file not found at {excel_file_path}")
            raise
        except Exception as e:
            print(f"Error reading Excel file {excel_file_path}: {e}")
            raise

    def map_column_names(self, instruction_set=None):
        """
        Maps the original Excel column names to standardized terms.

        Args:
            instruction_set (dict, optional): A dictionary to override or extend
                                              the default StandardEquipmentTerms.
                                              Format: {"Excel Column Name": "Standard Term"}
        """
        current_mapping_rules = StandardEquipmentTerms.copy()
        if instruction_set:
            current_mapping_rules.update(instruction_set)
            print(f"Applied custom instruction set for column mapping: {instruction_set}")

        self.mapped_columns = {}
        self.standardized_columns_to_extract = []
        processed_original_cols = set() # To handle cases where multiple original columns map to the same standard term

        # Prioritize instruction_set mappings
        if instruction_set:
            for original_col_df in self.original_columns:
                for instruction_col, standard_term in instruction_set.items():
                    if original_col_df.strip().lower() == instruction_col.strip().lower():
                        if standard_term not in self.standardized_columns_to_extract:
                            self.mapped_columns[original_col_df] = standard_term
                            self.standardized_columns_to_extract.append(standard_term)
                            processed_original_cols.add(original_col_df)
                        elif self.mapped_columns.get(original_col_df) != standard_term :
                             print(f"Warning: Column '{original_col_df}' was already mapped to '{self.mapped_columns.get(original_col_df)}'. "
                                   f"Instruction set trying to map it to '{standard_term}'. Keeping first mapping based on instruction priority or previous rule.")
                        break # Move to next original_col_df

        # Apply StandardEquipmentTerms for remaining columns
        for original_col_df in self.original_columns:
            if original_col_df in processed_original_cols:
                continue # Already mapped by instruction set

            original_col_lower = original_col_df.strip().lower()
            for potential_excel_col, standard_term in StandardEquipmentTerms.items():
                if original_col_lower == potential_excel_col.strip().lower():
                    if standard_term not in self.standardized_columns_to_extract:
                        self.mapped_columns[original_col_df] = standard_term
                        self.standardized_columns_to_extract.append(standard_term)
                        processed_original_cols.add(original_col_df)
                    elif self.mapped_columns.get(original_col_df) != standard_term:
                         print(f"Warning: Column '{original_col_df}' (matching '{potential_excel_col}') maps to '{standard_term}', "
                               f"but it might have already been mapped or another rule maps it differently. Check mappings.")
                    break # Found a match in StandardEquipmentTerms

        if not self.mapped_columns:
            print("Warning: No columns were successfully mapped. CSV output might be empty or only contain unmapped columns if logic changes.")
        else:
            print(f"Columns mapped: {self.mapped_columns}")
            print(f"Standardized columns to be used for CSV: {self.standardized_columns_to_extract}")


    def extract_to_csv(self, csv_file_path):
        """
        Extracts the data for the mapped columns and saves it to a CSV file.
        The CSV columns will be the standardized terms.

        Args:
            csv_file_path (str): The path to save the output CSV file.

        Raises:
            ValueError: If no columns have been mapped yet.
            Exception: For other potential errors during CSV writing.
        """
        if not self.mapped_columns:
            # If nothing was mapped, we might decide to write an empty CSV or all original columns.
            # For now, let's raise a warning and write what we have, which might be an empty df or original df.
            # This behavior can be adjusted based on more specific requirements.
            print("Warning: No columns were mapped. Attempting to write CSV, but it may be empty or not as expected.")
            # Option 1: Write an empty CSV with only standard headers if any were identified
            # df_to_save = pd.DataFrame(columns=self.standardized_columns_to_extract)
            # Option 2: Write the original dataframe if no mapping occurred (less ideal for standardization)
            # df_to_save = self.df.copy()
            # Option 3: Write only the columns that were successfully mapped, if any.
            # This is the current implemented logic path.
            if not self.standardized_columns_to_extract:
                 print(f"No standard columns identified for extraction. CSV file '{csv_file_path}' will be empty or only headers if provided.")
                 # Create an empty DataFrame with potential standard headers if any were decided upon even without mapping
                 # For now, let's create an empty df if no specific standard columns are set.
                 df_to_save = pd.DataFrame()
            else:
                # This case should ideally not be hit if self.mapped_columns is empty.
                # This implies self.standardized_columns_to_extract has values but self.mapped_columns is empty,
                # which indicates a logic flaw in map_column_names or its usage.
                # However, to be safe:
                df_to_save = pd.DataFrame(columns=self.standardized_columns_to_extract)


        # Create a new DataFrame with only the selected and renamed columns
        # We need to select columns from the original DataFrame whose original names are keys in self.mapped_columns
        # And then rename them to the values in self.mapped_columns

        # Filter self.df to include only columns that are keys in self.mapped_columns
        columns_to_select = [original_col for original_col in self.original_columns if original_col in self.mapped_columns]

        if not columns_to_select:
            print(f"No columns from the Excel file were successfully mapped to standard terms. Output CSV '{csv_file_path}' will likely be empty or headers only.")
            # Create an empty DataFrame with the desired standardized column names as headers
            df_to_save = pd.DataFrame(columns=list(set(self.mapped_columns.values()))) # Use set to ensure unique column names
        else:
            df_to_save = self.df[columns_to_select].copy()
            # Rename the columns to the standardized terms
            rename_dict = {original_col: self.mapped_columns[original_col] for original_col in columns_to_select}
            df_to_save.rename(columns=rename_dict, inplace=True)

            # Reorder columns to match the order in self.standardized_columns_to_extract if it's defined
            # and ensure all desired columns are present, adding missing ones with NaN
            final_columns_ordered = []
            # Use the values from mapped_columns which are the actual standard names intended for output
            # Ensure uniqueness and order if desired. For now, using the unique set of mapped standard names.
            desired_standard_names = list(dict.fromkeys(self.mapped_columns.values())) # Unique standard names, preserves order of first appearance

            for col_name in desired_standard_names:
                if col_name in df_to_save.columns:
                    final_columns_ordered.append(col_name)

            # If there are standard names that were mapped but somehow not in df_to_save (should not happen with current logic)
            # or if we want to ensure a specific order from a predefined list of ALL possible standard terms:
            # For now, just use the columns that are present and mapped.
            df_to_save = df_to_save[final_columns_ordered]


        try:
            df_to_save.to_csv(csv_file_path, index=False)
            print(f"Successfully extracted data to CSV: {csv_file_path}")
            print(f"CSV columns: {list(df_to_save.columns)}")
            return True
        except Exception as e:
            print(f"Error writing to CSV file {csv_file_path}: {e}")
            raise


# Step 3: Create the API for the agent
def process_excel(excel_file_path: str, output_csv_path: str, instruction_set: dict = None) -> bool:
    """
    Main API function to process an Excel file and convert it to a standardized CSV.

    Args:
        excel_file_path (str): Path to the input Excel file.
        output_csv_path (str): Path to save the output CSV file.
        instruction_set (dict, optional): Dictionary of custom column mappings.
                                          Format: {"Excel Column Name": "Standard Term"}

    Returns:
        bool: True if processing was successful and CSV was saved, False otherwise.
    """
    print(f"\nStarting Excel processing for: {excel_file_path}")
    print(f"Output CSV will be saved to: {output_csv_path}")
    if instruction_set:
        print(f"Using custom instruction set: {instruction_set}")

    try:
        processor = ExcelProcessor(excel_file_path)
        processor.map_column_names(instruction_set)
        processor.extract_to_csv(output_csv_path)
        print("Excel processing completed successfully.")
        return True
    except FileNotFoundError:
        print(f"Processing failed: Input Excel file not found at {excel_file_path}")
        return False
    except Exception as e:
        print(f"An error occurred during processing: {e}")
        return False

if __name__ == '__main__':
    print("--- Excel Processing Agent Demo ---")

    # Define file paths
    sample_excel_file = "sample_shipping_data.xlsx" # Created by create_sample_excel.py
    output_csv_default_mapping = "output_default_mapping.csv"
    output_csv_custom_mapping = "output_custom_mapping.csv"
    output_csv_no_mapping_found = "output_no_mapping_found.csv" # For testing unmapped scenario

    # Ensure the sample excel file exists (it should have been created by create_sample_excel.py)
    # For a standalone run, you might want to call a function that ensures its creation:
    # from create_sample_excel import create_sample_excel # Assuming it's in a separate file
    # create_sample_excel(sample_excel_file)

    print(f"\nScenario 1: Processing with default mappings.")
    print("-------------------------------------------------")
    success1 = process_excel(sample_excel_file, output_csv_default_mapping)
    if success1:
        print(f"Scenario 1 successfully created: {output_csv_default_mapping}")
        # Optionally, print contents of the CSV for verification
        try:
            df_check = pd.read_csv(output_csv_default_mapping)
            print("First 5 rows of the default mapped CSV:")
            print(df_check.head())
        except Exception as e:
            print(f"Could not read generated CSV for verification: {e}")
    else:
        print(f"Scenario 1 failed.")

    print(f"\nScenario 2: Processing with custom instruction set.")
    print("----------------------------------------------------")
    custom_instructions = {
        "ID": "ContainerID_Custom", # Override default for "ID"
        "Depot": "StorageLocation",   # Map "Depot" to a new standard term
        "Payload (kg)": "MaxPayload", # Map the specific "Payload (kg)" to "MaxPayload"
        "Extra Notes": "AdditionalDetails" # Map a column not in StandardEquipmentTerms
    }
    success2 = process_excel(sample_excel_file, output_csv_custom_mapping, instruction_set=custom_instructions)
    if success2:
        print(f"Scenario 2 successfully created: {output_csv_custom_mapping}")
        try:
            df_check_custom = pd.read_csv(output_csv_custom_mapping)
            print("First 5 rows of the custom mapped CSV:")
            print(df_check_custom.head())
        except Exception as e:
            print(f"Could not read generated CSV for verification: {e}")
    else:
        print(f"Scenario 2 failed.")

    print(f"\nScenario 3: Processing with an instruction set that results in no known mappings from StandardEquipmentTerms.")
    print("---------------------------------------------------------------------------------------------------------")
    # To simulate this, we can use an instruction set that points to columns not in the sample excel,
    # or maps to terms that won't match anything else if the primary mapping fails.
    # A more direct way is to use an excel with columns that don't match any rules.
    # For this test, let's use an instruction set that maps valid excel columns to terms
    # that are unique and won't be found in StandardEquipmentTerms (if not also defined in StandardEquipmentTerms)
    # or, more simply, try to process an excel with completely unrelated column names.

    # Let's create a dummy excel with non-matching column names for a cleaner test of "no mapping"
    try:
        dummy_data_for_no_mapping = pd.DataFrame({
            "ColA": [1, 2], "ColB": ["X", "Y"], "AnotherColumn": [True, False]
        })
        dummy_excel_no_mapping = "dummy_no_mapping.xlsx"
        dummy_data_for_no_mapping.to_excel(dummy_excel_no_mapping, index=False)

        print(f"Processing '{dummy_excel_no_mapping}' which has no columns matching default StandardEquipmentTerms.")
        success3 = process_excel(dummy_excel_no_mapping, output_csv_no_mapping_found)
        if success3:
            print(f"Scenario 3 processed for {dummy_excel_no_mapping}, created: {output_csv_no_mapping_found}")
            try:
                df_check_no_map = pd.read_csv(output_csv_no_mapping_found)
                print(f"Contents of '{output_csv_no_mapping_found}':")
                print(df_check_no_map) # Should be empty or only headers if any were decided
            except pd.errors.EmptyDataError:
                print(f"'{output_csv_no_mapping_found}' is empty as expected (no columns mapped).")
            except Exception as e:
                print(f"Error reading or verifying '{output_csv_no_mapping_found}': {e}")
        else:
            print(f"Scenario 3 failed to process (as expected if file error, or if it wrongly found mappings).")

    except Exception as e:
        print(f"Could not set up Scenario 3 for no mapping: {e}")


    print("\n--- Demo Complete ---")
