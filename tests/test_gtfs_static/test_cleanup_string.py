from gtfs_static.gtfs_static_utils import cleanup_string

def test_cleanup_string_none_value_as_input():
    """
    Check that if None value is given as input, None value is returned
    """
    assert cleanup_string(None) is None


def test_cleanup_string_empty_string_as_input():
    """
    Check that if an empty string is given as input, None value is returned
    """
    assert cleanup_string("") is None


def test_cleanup_string_whitespace_only_as_input():
    """
    Check that if only white spaces are given as input, None value is returned
    """
    assert cleanup_string("   ") is None


def test_cleanup_string_trimmed_string():
    """
    Check that if a string surrounded by white spaces is given as input,
    the white spaces are trimmed
    """
    assert cleanup_string("  test  ") == "test"


def test_cleanup_string_non_string_value():
    """
    Check that if a non-sring value is given as input, it is converted to string
    """
    assert cleanup_string(123) == "123"
