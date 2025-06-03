# EDI Analyzer Module
import collections
from typing import List, Dict, Optional, Any
# Assuming parser.py is in the same directory.
# If it's installed as part of the package, a relative import might be better:
# from .parser import parse_edi_message, get_delimiters
# For now, let's assume we might run this script directly for testing,
# so a simple import that works if the CWD is edi_eda/edi_eda/ might be okay.
# However, for package structure, relative imports are preferred.
# Let's adjust this if necessary based on how the execution environment is set up.

# For now, to make it runnable standalone if needed and also as part of a package,
# we can try a more flexible import strategy, though this can get complex.
# Let's assume for now the structure will be edi_eda.edi_eda.parser
try:
    from edi_eda.parser import parse_edi_message, get_delimiters # If run as part of edi_eda.edi_eda
except ImportError:
    try:
        from .parser import parse_edi_message, get_delimiters # If run from parent edi_eda directory
    except ImportError:
        # Fallback for direct execution or if PYTHONPATH is set up differently
        # This assumes parser.py is in the same directory as analyzer.py
        # This is less ideal for package distribution.
        import sys
        import os
        # Add the parent directory of the current file to sys.path
        # This allows importing sibling modules when the script is run directly.
        # sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        # from parser import parse_edi_message, get_delimiters
        # The above sys.path manipulation can be tricky.
        # Given the tool structure, it's best to assume the package structure will be handled
        # by the execution environment or later steps.
        # For now, let's rely on the most likely package import.
        pass # Will be handled by the actual execution context of the agent.


ParsedEDIData = List[List[str]]

def count_transaction_sets(parsed_edi_data: ParsedEDIData) -> collections.Counter:
    """
    Counts the occurrences of each transaction set ID in parsed EDI data.
    Transaction sets start with an 'ST' segment. ST01 is the transaction set ID.

    Args:
        parsed_edi_data: A list of segments, where each segment is a list of strings (elements).

    Returns:
        A collections.Counter object mapping transaction set IDs (str) to their counts (int).
    """
    transaction_counts = collections.Counter()
    if not parsed_edi_data:
        return transaction_counts

    for segment in parsed_edi_data:
        if segment and len(segment) > 1 and segment[0] == 'ST':
            transaction_id = segment[1]
            transaction_counts[transaction_id] += 1
    return transaction_counts

def get_segment_frequency(parsed_edi_data: ParsedEDIData) -> collections.Counter:
    """
    Counts the occurrences of each segment type in parsed EDI data.
    The segment type is the first element of a segment.

    Args:
        parsed_edi_data: A list of segments, where each segment is a list of strings (elements).

    Returns:
        A collections.Counter object mapping segment types (str) to their counts (int).
    """
    segment_counts = collections.Counter()
    if not parsed_edi_data:
        return segment_counts

    for segment in parsed_edi_data:
        if segment and segment[0]: # Check if segment is not empty and has a first element
            segment_id = segment[0]
            segment_counts[segment_id] += 1
    return segment_counts

def extract_element_values(
    parsed_edi_data: ParsedEDIData,
    segment_id: str,
    element_index: int,
    sub_element_separator: Optional[str] = None, # Added for clarity, will need to be passed
    sub_element_index: Optional[int] = None
) -> List[Optional[str]]:
    """
    Extracts specific element or sub-element values from parsed EDI data.

    Args:
        parsed_edi_data: A list of segments.
        segment_id: The ID of the segment to look for (e.g., 'DTM').
        element_index: The 1-based index of the element within the segment.
        sub_element_separator: The separator for sub-elements, required if sub_element_index is used.
        sub_element_index: The 1-based index of the sub-element within the element.

    Returns:
        A list of extracted values. Returns None for missing elements/sub-elements
        or if indices are out of bounds.
    """
    extracted_values: List[Optional[str]] = []
    if not parsed_edi_data:
        return extracted_values

    if element_index <= 0:
        # Or raise ValueError("Element index must be 1-based and positive.")
        return extracted_values # Or handle as an error

    actual_element_index = element_index - 1 # Convert to 0-based

    for segment in parsed_edi_data:
        if segment and segment[0] == segment_id:
            if actual_element_index < len(segment):
                element_value = segment[actual_element_index]
                if sub_element_index is not None:
                    if sub_element_index <= 0:
                        # Or raise ValueError("Sub-element index must be 1-based and positive.")
                        extracted_values.append(None) # Or handle as an error
                        continue
                    if not sub_element_separator:
                        # Or raise ValueError("Sub-element separator is required for sub-element extraction.")
                        extracted_values.append(None) # Or handle as an error
                        continue

                    actual_sub_element_index = sub_element_index - 1 # Convert to 0-based
                    sub_elements = element_value.split(sub_element_separator)
                    if actual_sub_element_index < len(sub_elements):
                        extracted_values.append(sub_elements[actual_sub_element_index])
                    else:
                        extracted_values.append(None) # Sub-element index out of bounds
                else:
                    extracted_values.append(element_value)
            else:
                extracted_values.append(None) # Element index out of bounds
    return extracted_values
