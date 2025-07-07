import pandas as pd

def create_sample_excel(file_path="sample_shipping_data.xlsx"):
    """Creates a sample Excel file for testing the ExcelProcessingAgent."""
    data = {
        "ID": ["CNTR001", "CNTR002", "CNTR003", "CNTR004", "CNTR005"],
        "Equipment Type": ["20GP", "40HC", "20RF", "40GP", "20OT"],
        "Size": [20, 40, 20, 40, 20],
        "Status": ["Available", "In Use", "Maintenance", "Available", "In Use"],
        "Depot": ["NYC01", "LAX02", "NYC01", "SFO03", "LAX02"],
        "Customer": ["CustA", "CustB", "N/A", "CustC", "CustA"],
        "Date of Last Move": pd.to_datetime(["2023-01-10", "2023-01-15", "2023-01-05", "2023-01-20", "2023-01-12"]),
        "Tare Weight": [2200, 3800, 2500, 3700, 2300],
        "Payload (kg)": [21800, 26680, 21500, 26780, 21700], # Note: "Payload (kg)" instead of "Max Payload" for testing mapping
        "Manufacture Date": pd.to_datetime(["2010-05-01", "2015-08-12", "2012-01-20", "2018-11-30", "2011-06-15"]),
        "Extra Notes": ["Good condition", "Needs cleaning", "Reefer unit check", "Minor dents", "Open top canvas new"],
        "MOS": ["Sea", "Rail", "Sea", "Road", "Sea"],
        "Means of Conveyance Authorization": ["VESSEL001", "TRAIN005", "VESSEL002", "TRUCK77", "BARGE03"], # Using a more verbose name for MEA
        "Carrier": ["CarrierX", "CarrierY", "CarrierX", "CarrierZ", "CarrierY"] # For IFC
    }
    df = pd.DataFrame(data)

    try:
        df.to_excel(file_path, index=False, engine='openpyxl') # Specify engine
        print(f"Sample Excel file '{file_path}' created successfully.")
    except Exception as e:
        print(f"Failed to create sample Excel file: {e}")

if __name__ == '__main__':
    create_sample_excel()
