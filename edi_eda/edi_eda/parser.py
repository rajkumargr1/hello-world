# EDI Parser Module
import os

def read_edi_file(file_path: str) -> str:
    """
    Reads an EDI file and returns its content as a string.

    Args:
        file_path: The path to the EDI file.

    Returns:
        The content of the EDI file as a string.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    try:
        with open(file_path, 'r') as f:
            edi_content = f.read()
        return edi_content
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: File not found at {file_path}")

def get_delimiters(edi_content: str) -> tuple[str, str, str]:
    """
    Inspects the ISA segment to determine delimiters.
    Defaults to common delimiters if ISA is not found or is too short.

    Args:
        edi_content: The EDI message as a string.

    Returns:
        A tuple containing (segment_terminator, element_separator, sub_element_separator).
    """
    default_segment_terminator = '~'
    default_element_separator = '*'
    default_sub_element_separator = ':'

    if edi_content.startswith("ISA") and len(edi_content) >= 106:
        element_separator = edi_content[3]
        # The 106th character (index 105) is the segment terminator.
        segment_terminator = edi_content[105]
        # The 105th character (index 104) is the sub-element separator (repetition separator in X12).
        sub_element_separator = edi_content[104]
        return segment_terminator, element_separator, sub_element_separator
    else:
        # Attempt to infer from the first few segments if ISA is not standard
        # This is a simplified inference, real-world EDI can be more complex
        if not edi_content:
            return default_segment_terminator, default_element_separator, default_sub_element_separator

        potential_segment_terminator = ''
        for char_code in range(ord('~'), 31, -1): # Check common non-printable and printable chars
            char = chr(char_code)
            if char.isprintable() and not char.isalnum() and char in edi_content:
                if edi_content.count(char) > 1 : # Likely a segment terminator if it appears multiple times
                    potential_segment_terminator = char
                    break

        segment_terminator = potential_segment_terminator if potential_segment_terminator else default_segment_terminator

        # Try to find element separator in the first segment (assuming it's not ISA)
        first_segment_end = edi_content.find(segment_terminator)
        first_segment = edi_content
        if first_segment_end != -1:
            first_segment = edi_content[:first_segment_end]

        potential_element_separator = ''
        # Check common non-alphanumeric characters as potential element separators
        common_separators = ['*', ':', '^', '|'] # Add more if needed
        for sep in common_separators:
            if sep in first_segment and sep != segment_terminator:
                potential_element_separator = sep
                break

        element_separator = potential_element_separator if potential_element_separator else default_element_separator

        # For sub-element separator, we'll stick to default or a common one if not ISA
        # as it's harder to infer reliably without ISA segment.
        # If element_separator is ':', try '^' or vice versa, otherwise default.
        if element_separator == default_sub_element_separator:
            sub_element_separator = '^'
        else:
            sub_element_separator = default_sub_element_separator

        return segment_terminator, element_separator, sub_element_separator


def parse_edi_message(edi_content: str, segment_terminator: str, element_separator: str) -> list[list[str]]:
    """
    Parses an EDI message string into a list of segments, where each segment
    is a list of its data elements.

    Args:
        edi_content: The EDI message as a string.
        segment_terminator: The character used to terminate segments.
        element_separator: The character used to separate data elements.

    Returns:
        A list of segments, where each segment is a list of strings (elements).
        Returns an empty list if the edi_content is empty or None.
    """
    if not edi_content:
        return []

    # Remove any leading/trailing whitespace from the content
    edi_content = edi_content.strip()

    # If the content ends with a segment terminator, split will produce an empty string at the end.
    # We should remove it if it's there.
    segments = edi_content.split(segment_terminator)
    if segments and segments[-1] == '':
        segments.pop()

    parsed_segments = []
    for segment_str in segments:
        if segment_str:  # Handle potential empty segments
            elements = segment_str.split(element_separator)
            # Handle potential empty elements by replacing them with empty strings
            # though split already does this. This is more for clarity.
            parsed_segments.append([element if element else "" for element in elements])
        else:
            # If it's an empty segment string (e.g. consecutive terminators), add an empty list
            parsed_segments.append([])

    return parsed_segments
