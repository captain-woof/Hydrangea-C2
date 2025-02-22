import base64
import datetime

def convertUnixTimeToHumanReadable(unixTimeSecs):
    """
    Parses a time input (Unix milliseconds or Unix seconds) and returns a human-readable datetime string.

    Args:
        time_input: The time input, which can be:
            - An integer representing Unix milliseconds or seconds.
            - A string representing Unix milliseconds or seconds as a number.

    Returns:
        A string representing the date and time in a human-readable format (e.g., "YYYY-MM-DD HH:MM:SS UTC").

    Raises:
        TypeError: If the input is not an integer or a string.
        ValueError: If the input string cannot be converted to a number or
                    if the parsed timestamp is invalid (e.g., out of range).
        Exception: For other unexpected errors during time conversion.
    """

    if not isinstance(unixTimeSecs, (int, str)):
        raise TypeError("Input must be an integer or a string representing Unix time.")

    try:
        timestamp_numeric = float(unixTimeSecs)  # Attempt to convert string to number
    except ValueError:
        raise ValueError("Invalid input string: Cannot convert to a numeric timestamp.")

    if timestamp_numeric < 0:
        raise ValueError("Invalid timestamp: Unix time cannot be negative.")

    try:
        datetime_object_utc = datetime.datetime.fromtimestamp(timestamp_numeric)
        human_readable_time = datetime_object_utc.strftime("%Y-%m-%d %H:%M:%S")  # Format as YYYY-MM-DD HH:MM:SS

        return human_readable_time

    except ValueError as ve:
        raise ValueError(f"Invalid timestamp value: {ve}") # Re-raise ValueError for invalid datetime ranges
    except Exception as e:
        raise Exception(f"An unexpected error occurred during time parsing: {e}")

def base64Encode(s: str):
    return base64.b64encode(s.encode("utf-8") if type(s) == "str" else s).decode("utf-8")

def base64Decode(s: str):
    return base64.b64decode(s.encode("utf-8") if type(s) == "str" else s).decode("utf-8")

def stringSplitAdvanced(strInput):
    """
    Splits a UTF-8 string by spaces, treating substrings enclosed in " or ' as single units.
    Escaped quotes (\\", \\') within their respective quotes do not end the substring.

    Args:
        input_string: The UTF-8 string to split.

    Returns:
        A list of strings representing the split result.
    """
    result = []
    current_word = ""
    quote_type = None  # None, '"', or "'"
    escape = False

    for char in strInput:
        if escape:
            current_word += char
            escape = False
            continue

        if char == '\\':
            escape = True
            continue

        if quote_type:  # Inside a quote
            if char == quote_type:
                result.append(current_word)
                current_word = ""
                quote_type = None
            else:
                current_word += char
        else:  # Not inside a quote
            if char == ' ':
                if current_word:  # Add word if it's not empty
                    result.append(current_word)
                    current_word = ""
            elif char == '"':
                quote_type = '"'
                current_word = "" # Start a new word
            elif char == "'":
                quote_type = "'"
                current_word = "" # Start a new word
            else:
                current_word += char

    # Add the last word if any
    if current_word:
        result.append(current_word)

    return result

def dictArrayToTable(dictArray):
    """
    Converts an array of dictionaries to a formatted table string.

    Args:
        dict_array: A list of dictionaries. All dictionaries must have the same keys.

    Returns:
        A string representing the table, or an empty string if the input is empty.

    Raises:
        TypeError: if input is not a list or contains non-dictionary elements.
        ValueError: if dictionaries in the array do not have the same keys.
    """

    if not isinstance(dictArray, list):
        raise TypeError("Input must be a list of dictionaries.")

    if not dictArray:
        return ""  # Return empty string for empty input

    # Validate that all elements are dictionaries and get keys from the first dictionary
    if not isinstance(dictArray[0], dict):
        raise TypeError("Input list must contain only dictionaries.")
    expected_keys = set(dictArray[0].keys())

    for i in range(1, len(dictArray)):
        if not isinstance(dictArray[i], dict):
            raise TypeError("Input list must contain only dictionaries.")
        current_keys = set(dictArray[i].keys())
        if current_keys != expected_keys:
            raise ValueError("Dictionaries in the input array must have the same keys.")

    headers = list(expected_keys)
    column_widths = {}

    # Initialize column widths with header lengths
    for header in headers:
        column_widths[header] = len(str(header))

    # Calculate column widths based on data in dictionaries
    for dictionary in dictArray:
        for key, value in dictionary.items():
            column_widths[key] = max(column_widths[key], len(str(value)))

    # Construct table string
    output_string = ""

    # Header row
    header_row = "|"
    for header in headers:
        header_row += " " + str(header).ljust(column_widths[header]) + " |"
    output_string += header_row + "\n"

    # Separator row
    separator_row = "+"
    for header in headers:
        separator_row += "-" * (column_widths[header] + 2) + "+"
    output_string += separator_row + "\n"

    # Data rows
    for dictionary in dictArray:
        data_row = "|"
        for header in headers:
            value = dictionary.get(header, "")  # Handle missing keys gracefully (though keys are validated to be the same)
            data_row += " " + str(value).ljust(column_widths[header]) + " |"
        output_string += data_row + "\n"

    # Separator row at the end
    output_string += separator_row + "\n"

    return output_string