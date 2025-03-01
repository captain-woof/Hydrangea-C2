import base64
import random
import string
import datetime

def base64Encode(s: str, outputString = True):
    encodedBytes = base64.b64encode(s.encode("utf-8") if isinstance(s, str) else s)
    if outputString:
        return encodedBytes.decode("utf-8")
    else:
        return encodedBytes

def base64Decode(s: str, outputString = True):
    encodedBytes = base64.b64decode(s.encode("utf-8") if isinstance(s, str) else s)
    if outputString:
        return encodedBytes.decode("utf-8")
    else:
        return encodedBytes
    
def generateRandomStr(strLen: int):
    return "".join([random.choice(string.ascii_letters) for _ in range(0, strLen)])

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