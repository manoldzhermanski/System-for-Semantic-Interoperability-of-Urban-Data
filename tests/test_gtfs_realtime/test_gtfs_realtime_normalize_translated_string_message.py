from gtfs_realtime.gtfs_realtime_utils import gtfs_realtime_normalize_translated_string_message

def test_normalize_translated_string_with_translations():
    """
    Check that a TranslatedString message is given, the function
    extracts the list of "text-language" dictionaries
    """
    entity = {
        "cause_detail": {
            "translation": [
                {"text": "Delay", "language": "en"},
                {"text": "Закъснение", "language": "bg"},
            ]
        }
    }

    result = gtfs_realtime_normalize_translated_string_message(entity=entity,field="cause_detail")

    expected = [
        {"text": "Delay", "language": "en"},
        {"text": "Закъснение", "language": "bg"}
    ]
    
    assert result == expected


def test_normalize_translated_string_missing_field():
    """
    Check that if a TranslatedString message is empty, a empty list is returned
    """
    result = gtfs_realtime_normalize_translated_string_message(entity={}, field="cause_detail")

    assert result == []


def test_normalize_translated_string_entity_none():
    """
    Check that if a TranslatedString message is None, a empty list is returned
    """
    result = gtfs_realtime_normalize_translated_string_message(entity=None,field="cause_detail")

    assert result == []


def test_normalize_translated_string_empty_translation():
    """
    Check that if the 'translation' field in a TranslatedString message is empty,
    a empty list is returned
    """
    entity = {
        "cause_detail": {
            "translation": []
        }
    }

    result = gtfs_realtime_normalize_translated_string_message(entity=entity, field="cause_detail")

    assert result == []
