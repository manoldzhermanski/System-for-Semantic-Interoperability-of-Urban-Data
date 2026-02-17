import re
import pycountry
import validators
from zoneinfo import ZoneInfo
from datetime import datetime
from typing import Any

# -----------------------------------------------------
# Number checks
# -----------------------------------------------------
def is_valid_currency_price(value: Any) -> bool:
    # Must be int or float
    if not isinstance(value, (int, float)):
        return False

    # Must be non-negative
    if value < 0:
        return False

    # Must have at most 2 decimal places
    return round(value, 2) == value


# -----------------------------------------------------
# String checks
# -----------------------------------------------------

def is_valid_url(url: Any) -> bool:
    """
    Check if argument is a valid URL

    Args:
        url (Any): Argument to check

    Returns:
        bool: True if valid URL, False otherwise
    """
    
    # Return False, if not a string
    if not isinstance(url, str):
        return False

    # Remove white spaces around the string
    url = url.strip()
    
    # Return False, if empty string
    if url == "":
        return False
    
    # if valid, result is True, otherwise ValidationError
    result = validators.url(url)
    
    # Return True if result is True, otherwise False
    return result is True

def is_valid_email(email: Any) -> bool:
    """
    Check if argument is a valid email address

    Args:
        email (Any): Argument to check

    Returns:
        bool: True if valid email, False otherwise
    """
    # Return False, if not a string
    if not isinstance(email, str):
        return False

    # Remove white spaces around the string
    email = email.strip()
        
    # Return False, if empty string
    if email == "":
        return False
    
    # if valid, result is True, otherwise ValidationError
    result = validators.email(email)
    
    # Return True if result is True, otherwise False
    return result is True

def is_valid_phone_number(number: Any) -> bool:
    """
    Check if argument is a valid phone number
    Args:
        number (Any): Argument to check

    Returns:
        bool: True if argument is a valid phone number, otherwise False
    """
    # Return False, if not a string
    if not isinstance(number, str):
        return False

    # Remove white spaces around the string
    number = number.strip()

    # Return False, if empty string
    if number == "":
        return False

    # Check if at least one digit is present
    if not any(ch.isdigit() for ch in number):
        return False

    # Allowed characters: digits, letters, + - ( ) space
    if not re.fullmatch(r"[0-9A-Za-z+\-\(\)\s/]+", number):
        return False
    
    # If all checks passed, return True
    return True

def is_valid_color(color_code: Any) -> bool:
    """
    Check if argument is a six-digit hex code depicting a color
    
    Args:
        color_code (Any): Argument to check

    Returns:
        bool: True if Argument is a valid six-digit hex code, otherwise False
    """
    # Return False, if not a string
    if not isinstance(color_code, str):
        return False
    
    # Remove white spaces around the string
    color_code = color_code.strip()
    
    # Return False, if empty string
    if color_code == "":
        return False

    # True if string is a valid six-digit hex code, otherwise False
    return bool(re.fullmatch(r"[A-Fa-f0-9]{6}", color_code))

# -----------------------------------------------------
# Timezone check
# -----------------------------------------------------

def is_valid_timezone(timezone: Any) -> bool:
    """
    Check if argument is a valid timezone code

    Args:
        timezone (Any): Argument to check

    Returns:
        bool: True if argument is valid timezone, False otherwise
    """
        # Return False, if not a string
    if not isinstance(timezone, str):
        return False
    
    # Remove white spaces around the string
    timezone = timezone.strip()
    
    # Return False, if empty string
    if timezone == "":
        return False
    
    try:
        # Attempt to parse string as a timezone 
        ZoneInfo(timezone)
        return True
    except Exception:
        # If parsing fails, the string is not a valid timezone
        return False

# -----------------------------------------------------
# Country Code Checks
# -----------------------------------------------------
    
def is_valid_currency_code(value: Any) -> bool:
    """
    Check if argument is a valid currency code

    Args:
        value (Any): Argument to check

    Returns:
        bool: True if argument is valid currency string, False otherwise
    """
    # Return False, if not a string
    if not isinstance(value, str):
        return False
    
    # Remove white spaces around string and turn it uppercase
    value = value.strip()
    
    # Check if currency code is upper case
    if value.upper() != value:
        return False

    # Return False, if empty string
    if value == "":
        return False
    
    # Return True if string is a valid currency code comprised of 3 letters, False otherwise
    return pycountry.currencies.get(alpha_3=value) is not None

def is_valid_language_code(code: Any) -> bool:
    """
    Check if argument is a valid language code

    Args:
        code (Any): Argument to check

    Returns:
        bool: True if valid language code, False otherwise
    """
    # Return False, if not a string
    if not isinstance(code, str):
        return False
    
    # Remove white spaces around the string
    code = code.strip()
    
    # Check if language code is lower case
    if code.lower() != code:
        return False
    
    # Return False, if empty string
    if code == "":
        return False
    
    # True if string is a 2 letter language code
    if pycountry.languages.get(alpha_2=code):
        return True
    
    # True if string is 3 letter language code
    if pycountry.languages.get(alpha_3=code):
        return True
    
    # Otherwise not a language code
    return False

# -----------------------------------------------------
# Enum Checks
# -----------------------------------------------------

def is_valid_cemv_support(value: Any) -> bool:
    """
    Check if argument is a valid enum value for 'cemv_support'

    Args:
        value (Any): Argument to check
    Returns:
        bool: True if value in enum range, False otherwise
    """
    if type(value) is not int:
        return False
    return value in {0, 1, 2}
          
def is_valid_exception_type(value: Any) -> bool:
    """
    Check if argument is a valid enum value for 'exception_type' field

    Args:
        value (Any): Argment to check
    Returns:
        bool: True if value in enum range, False otherwise
    """
    if type(value) is not int:
        return False
    return value in {1, 2}

def is_valid_payment_method(value: Any) -> bool:
    """
    Check if argument is a valid enum value for 'payment_method' field

    Args:
        value (Any): Argument to check
    Returns:
        bool: True if value in enum range, False otherwise
    """
    if type(value) is not int:
        return False
    return value in {0, 1}

def is_valid_transfers(value: Any) -> bool:
    """
    Check if argument is a valid enum value for 'transfers'

    Args:
        value (Any): Argument to check
    Returns:
        bool: True if value in enum range, False otherwise
    """
    if type(value) is not int:
        return False
    return value in {-1, 0, 1, 2}

def is_valid_pathway_mode(value: Any) -> bool:
    """
    Check if argument is a valid enum value for 'pathway_mode'

    Args:
        value (Any): Argument to check
    Returns:
        bool: True if value in enum range, False otherwise
    """
    if type(value) is not int:
        return False
    return value in {1, 2, 3, 4, 5, 6, 7}

def is_valid_is_bidirectional(value: Any) -> bool:
    """
    Check if argument is a valid enum value for 'is_bidirectional'

    Args:
        value (Any): Argument to check
    Returns:
        bool: True if value in enum range, False otherwise
    """
    if type(value) is not int:
        return False
    return value in {0, 1}

def is_valid_route_type(value: Any) -> bool:
    """
    Check if argument is a valid enum value for 'route_type'

    Args:
        value (Any): Argument to check
    Returns:
        bool: True if value in enum range, False otherwise
    """
    if type(value) is not int:
        return False
    return value in {0, 1, 2, 3, 4, 5, 6, 7, 11, 12, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112,
                     113, 114, 115, 116, 117, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 400, 401, 402, 403, 404,
                     405, 700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 710, 711, 712, 713, 714, 715, 716, 800, 900,
                     901, 902, 903, 904, 905, 906, 1000, 1100, 1200, 1300, 1301, 1302, 1303, 1304, 1305, 1306, 1307, 1400,
                     1500, 1501, 1502, 1503, 1504, 1505, 1506, 1507, 1700, 1702}

def is_valid_continuous_pickup(value: Any) -> bool:
    """
    Check if argument is a valid enum value for 'continuous_pickup'

    Args:
        value (Any): Argument to check
    Returns:
        bool: True if value in enum range, False otherwise
    """
    if type(value) is not int:
        return False
    return value in {0, 1, 2, 3}

def is_valid_continuous_drop_off(value: Any) -> bool:
    """
    Check if argument is a valid enum value for 'continuous_drop_off'

    Args:
        value (Any): Argument to check
    Returns:
        bool: True if value in enum range, False otherwise
    """
    if type(value) is not int:
        return False
    return value in {0, 1, 2, 3}

def is_valid_pickup_type(value: Any) -> bool:
    """
    Check if argument is a valid enum value for 'pickup_type'

    Args:
        value (Any): Argument to check
    Returns:
        bool: True if value in enum range, False otherwise
    """
    if type(value) is not int:
        return False
    return value in {0, 1, 2, 3}
    
def is_valid_drop_off_type(value: Any) -> bool:
    """
    Check if argument is a valid enum value for 'drop_off_type'

    Args:
        value (Any): Argument to check
    Returns:
        bool: True if value in enum range, False otherwise
    """
    if type(value) is not int:
        return False
    return value in {0, 1, 2, 3}

def is_valid_location_type(value: Any) -> bool:
    """
    Check if argument is a valid enum value for 'location_type'

    Args:
        value (Any): Argument to check
    Returns:
        bool: True if value in enum range, False otherwise
    """
    if type(value) is not int:
        return False
    return value in {0, 1, 2, 3, 4}

def is_valid_wheelchair_boarding(value: Any) -> bool:
    """
    Check if argument is a valid enum value for 'wheelchair_boarding'

    Args:
        value (Any): Argument to check
    Returns:
        bool: True if value in enum range, False otherwise
    """
    if type(value) is not int:
        return False
    return value in {0, 1, 2}

def is_valid_stop_access(value: Any) -> bool:
    """
    Check if argument is a valid enum value for 'stop_access'

    Args:
        value (Any): Argument to check
    Returns:
        bool: True if value in enum range, False otherwise
    """
    if type(value) is not int:
        return False
    return value in {0, 1}

def is_valid_transfer_type(value: Any) -> bool:
    """
    Check if argument is a valid enum value for 'transfer_type'

    Args:
        value (Any): Argument to check
    Returns:
        bool: True if value in enum range, False otherwise
    """
    if type(value) is not int:
        return False
    return value in {0, 1, 2, 3, 4, 5}

def is_valid_direction_id(value: Any) -> bool:
    """
    Check if argument is a valid enum value for 'direction_id'

    Args:
        value (Any): Argument to check
    Returns:
        bool: True if value in enum range, False otherwise
    """
    if type(value) is not int:
        return False
    return value in {0, 1}

def is_valid_wheelchair_accessible(value: Any) -> bool:
    """
    Check if argument is a valid enum value for 'wheelchair_accessible'

    Args:
        value (Any): Argument to check
    Returns:
        bool: True if value in enum range, False otherwise
    """
    if type(value) is not int:
        return False
    return value in {0, 1, 2}

def is_valid_bikes_allowed(value: Any) -> bool:
    """
    Check if argument is a valid enum value for 'bikes_allowed'

    Args:
        value (Any): Argument to check
    Returns:
        bool: True if value in enum range, False otherwise
    """
    if type(value) is not int:
        return False
    return value in {0, 1, 2}

def is_valid_cars_allowed(value: Any) -> bool:
    """
    Check if argument is a valid enum value for 'cars_allowed'

    Args:
        value (Any): Argument to check
    Returns:
        bool: True if value in enum range, False otherwise
    """
    if type(value) is not int:
        return False
    return value in {0, 1, 2}

def is_valid_timepoint(value: Any) -> bool:
    """
    Check if argument is a valid enum value for 'timepoint'

    Args:
        value (Any): Argument to check
    Returns:
        bool: True if value in enum range, False otherwise
    """
    if type(value) is not int:
        return False
    return value in {0, 1}