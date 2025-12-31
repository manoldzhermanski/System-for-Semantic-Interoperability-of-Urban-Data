from gtfs_realtime.gtfs_realtime_utils import normalize_keys_to_snake_case

def test_normalize_keys_to_snake_case_simple_key():
    """
    Check that a key with a single word is written as lower case
    """
    entity = {"Alert": 1}
    
    expected = {"alert": 1}
    result = normalize_keys_to_snake_case(entity)

    assert result == expected

def test_normalize_keys_to_snake_case_camel_case_key():
    """
    Check that if a key is composed of 2 words, it's written in snake case
    """
    entity = {"activePeriod": 123}
    expected = {"active_period": 123}
    
    result = normalize_keys_to_snake_case(entity)

    assert result == expected

def test_normalize_keys_to_snake_case_nested_dict():
    """
    Check that the keys of nested dictionaries are written in snake case
    """
    entity = {"Alert": {"activePeriod": 123}}
    expected = {"alert": {"active_period": 123}}

    result = normalize_keys_to_snake_case(entity)

    assert result == expected

def test_normalize_keys_to_snake_case_list_of_dicts():
    """
    Check that complex structes are traversed and all keys are converted to snake case
    """
    entity = {
        "InformedEntity": [
            {"TripId": "123"},
            {"TripId": "456"},
        ]
    }
    
    expected = {
        "informed_entity": [
            {"trip_id": "123"},
            {"trip_id": "456"},
        ]
    }

    result = normalize_keys_to_snake_case(entity)

    assert result == expected

def test_normalize_keys_to_snake_case_already_snake_case():
    """
    Check that if all keys are already in snake case, nothing is changed
    """
    entity = {
        "active_period": {
            "start_time": "08:00"
        }
    }

    result = normalize_keys_to_snake_case(entity)

    assert result == entity


def normalize_keys_to_snake_case_gtfs_realtime_vehicle_position():
    entity = {
        "id": "TM29-TM1448-2-7-12489740050",
        "vehicle": {
            "trip": {
            "tripId": "TM29-TM1448-2-7-12489740050",
            "scheduleRelationship": "SCHEDULED",
            "routeId": "TM29"
            },
            "position": {
                "latitude": 42.66788,
                "longitude": 23.26594,
                "speed": 20.0
            },
            "currentStatus": "IN_TRANSIT_TO",
            "timestamp": "1767173265",
            "congestionLevel": "UNKNOWN_CONGESTION_LEVEL",
            "stopId": "TM0348",
            "vehicle": {
                "id": "TM0932"
            },
            "occupancyStatus": "EMPTY"
            }
        }
    
    expected = {
        "id": "TM29-TM1448-2-7-12489740050",
        "vehicle": {
            "trip": {
            "trip_id": "TM29-TM1448-2-7-12489740050",
            "schedule_relationship": "SCHEDULED",
            "route_id": "TM29"
            },
            "position": {
                "latitude": 42.66788,
                "longitude": 23.26594,
                "speed": 20.0
            },
            "current_status": "IN_TRANSIT_TO",
            "timestamp": "1767173265",
            "congestion_level": "UNKNOWN_CONGESTION_LEVEL",
            "stop_id": "TM0348",
            "vehicle": {
                "id": "TM0932"
            },
            "occupancy_status": "EMPTY"
            }
        }
    
    result = normalize_keys_to_snake_case(entity)
    
    assert result == expected
    
def normalize_keys_to_snake_case_gtfs_realtime_trip_update():
    entity = {
        "id": "TB35-TB915-3-8-13037154010",
        "isDeleted": False,
        "tripUpdate": {
            "trip": {
            "tripId": "TB35-TB915-3-8-13037154010",
            "scheduleRelationship": "SCHEDULED",
            "routeId": "TB35"
            },
            "stopTimeUpdate": [
                {
                    "arrival": {
                        "time": "1767173952",
                        "uncertainty": 0
                        },
                    "departure": {
                        "time": "1767173952",
                        "uncertainty": 0
                        },
                    "stopId": "TB1845",
                    "scheduleRelationship": "SCHEDULED"
                    },
                {
                    "arrival": {
                        "time": "1767174012",
                        "uncertainty": 0
                        },
                    "departure": {
                        "time": "1767174012",
                        "uncertainty": 0
                        },
                    "stopId": "TB0069",
                    "scheduleRelationship": "SCHEDULED"
                    },
                {
                    "arrival": {
                        "time": "1767174081",
                        "uncertainty": 0
                        },
                    "departure": {
                        "time": "1767174081",
                        "uncertainty": 0
                        },
                    "stopId": "TB1566",
                    "scheduleRelationship": "SCHEDULED"
                    },
                {
                    "arrival": {
                        "time": "1767174131",
                        "uncertainty": 0
                        },
                    "departure": {
                        "time": "1767174131",
                        "uncertainty": 0
                        },
                    "stopId": "TB0813",
                    "scheduleRelationship": "SCHEDULED"
                    },
                {
                    "arrival": {
                        "time": "1767174226",
                        "uncertainty": 0
                        },
                    "departure": {
                        "time": "1767174226",
                        "uncertainty": 0
                        },
                    "stopId": "TB0227",
                    "scheduleRelationship": "SCHEDULED"
                    },
                {
                    "arrival": {
                        "time": "1767174296",
                        "uncertainty": 0
                        },
                    "departure": {
                        "time": "1767174296",
                        "uncertainty": 0
                        },
                    "stopId": "TB0231",
                    "scheduleRelationship": "SCHEDULED"
                    },
                {
                    "arrival": {
                        "time": "1767174410",
                        "uncertainty": 0
                        },
                    "departure": {
                        "time": "1767174410",
                        "uncertainty": 0
                        },
                    "stopId": "TB2141",
                    "scheduleRelationship": "SCHEDULED"
                    },
                {
                    "arrival": {
                        "time": "1767174464",
                        "uncertainty": 0
                        },
                    "departure": {
                        "time": "1767174464",
                        "uncertainty": 0
                        },
                    "stopId": "TB0192",
                    "scheduleRelationship": "SCHEDULED"
                     },
                {
                    "arrival": {
                        "time": "1767174518",
                        "uncertainty": 0
                        },
                    "departure": {
                        "time": "1767174518",
                        "uncertainty": 0
                        },
                    "stopId": "TB0175",
                    "scheduleRelationship": "SCHEDULED"
                    },
                {
                    "arrival": {
                        "time": "1767174598",
                        "uncertainty": 0
                        },
                    "departure": {
                        "time": "1767174598",
                        "uncertainty": 0
                        },
                    "stopId": "TB1708",
                    "scheduleRelationship": "SCHEDULED"
                    },
                {
                    "arrival": {
                        "time": "1767174643",
                        "uncertainty": 0
                        },
                    "departure": {
                        "time": "1767174643",
                        "uncertainty": 0
                        },
                    "stopId": "TB0682",
                    "scheduleRelationship": "SCHEDULED"
                    }
                ],
            "timestamp": "1767173887"
            }
        }
    
    expected = {
        "id": "TB35-TB915-3-8-13037154010",
        "is_deleted": False,
        "trip_update": {
            "trip": {
            "trip_id": "TB35-TB915-3-8-13037154010",
            "schedule_relationship": "SCHEDULED",
            "route_id": "TB35"
            },
            "stop_time_update": [
                {
                    "arrival": {
                        "time": "1767173952",
                        "uncertainty": 0
                        },
                    "departure": {
                        "time": "1767173952",
                        "uncertainty": 0
                        },
                    "stop_id": "TB1845",
                    "schedule_relationship": "SCHEDULED"
                    },
                {
                    "arrival": {
                        "time": "1767174012",
                        "uncertainty": 0
                        },
                    "departure": {
                        "time": "1767174012",
                        "uncertainty": 0
                        },
                    "stop_id": "TB0069",
                    "schedule_relationship": "SCHEDULED"
                    },
                {
                    "arrival": {
                        "time": "1767174081",
                        "uncertainty": 0
                        },
                    "departure": {
                        "time": "1767174081",
                        "uncertainty": 0
                        },
                    "stop_id": "TB1566",
                    "schedule_relationship": "SCHEDULED"
                    },
                {
                    "arrival": {
                        "time": "1767174131",
                        "uncertainty": 0
                        },
                    "departure": {
                        "time": "1767174131",
                        "uncertainty": 0
                        },
                    "stop_id": "TB0813",
                    "schedule_relationship": "SCHEDULED"
                    },
                {
                    "arrival": {
                        "time": "1767174226",
                        "uncertainty": 0
                        },
                    "departure": {
                        "time": "1767174226",
                        "uncertainty": 0
                        },
                    "stop_id": "TB0227",
                    "schedule_relationship": "SCHEDULED"
                    },
                {
                    "arrival": {
                        "time": "1767174296",
                        "uncertainty": 0
                        },
                    "departure": {
                        "time": "1767174296",
                        "uncertainty": 0
                        },
                    "stop_id": "TB0231",
                    "schedule_relationship": "SCHEDULED"
                    },
                {
                    "arrival": {
                        "time": "1767174410",
                        "uncertainty": 0
                        },
                    "departure": {
                        "time": "1767174410",
                        "uncertainty": 0
                        },
                    "stop_id": "TB2141",
                    "schedule_relationship": "SCHEDULED"
                    },
                {
                    "arrival": {
                        "time": "1767174464",
                        "uncertainty": 0
                        },
                    "departure": {
                        "time": "1767174464",
                        "uncertainty": 0
                        },
                    "stopId": "TB0192",
                    "schedule_relationship": "SCHEDULED"
                     },
                {
                    "arrival": {
                        "time": "1767174518",
                        "uncertainty": 0
                        },
                    "departure": {
                        "time": "1767174518",
                        "uncertainty": 0
                        },
                    "stop_id": "TB0175",
                    "schedule_relationship": "SCHEDULED"
                    },
                {
                    "arrival": {
                        "time": "1767174598",
                        "uncertainty": 0
                        },
                    "departure": {
                        "time": "1767174598",
                        "uncertainty": 0
                        },
                    "stop_id": "TB1708",
                    "schedule_relationship": "SCHEDULED"
                    },
                {
                    "arrival": {
                        "time": "1767174643",
                        "uncertainty": 0
                        },
                    "departure": {
                        "time": "1767174643",
                        "uncertainty": 0
                        },
                    "stop_id": "TB0682",
                    "schedule_relationship": "SCHEDULED"
                    }
                ],
            "timestamp": "1767173887"
            }
        }
    
    result = normalize_keys_to_snake_case(entity)
    
    assert result == expected
    
def normalize_keys_to_snake_case_gtfs_realtime_trip_alerts():
    entity = {
        "id": "fee63522-e3d5-4bdd-b6b7-92365577e84f",
        "alert": {
            "activePeriod": [
                {
                    "start": "1760313600",
                    "end": "1768203600"
                    }
                ],
            "informedEntity": [
                {
                    "routeId": "TM50"
                    }
                ],
            "cause": "OTHER_CAUSE",
            "effect": "STOP_MOVED",
            "url": {
                "translation": [
                    {
                        "text": "https://sofiatraffic.bg/bg",
                        "language": "bg"
                        },
                    {
                        "text": "https://sofiatraffic.bg/en",
                        "language": "en"
                        }
                    ]
                },
            "headerText": {
                "translation": [
                    {
                        "text": "",
                        "language": "bg"
                        },
                    {
                        "text": "",
                        "language": "en"
                        }
                    ]
                },
            "descriptionText": {
                "translation": [
                    {
                        "text": "<p>От 17:00 часа на 13.10.2025 г. спирка с код 2587 „Ул. Амстердам“ за трамвайна линия № 23 на бул. „Копенхаген“ след ул. Амстердам“ в посока ул. „Обиколна“ временно се закрива.</p>",
                        "language": "bg"
                        },
                    {
                        "text": "<p><span>From 17:00 on October 13, 2025 to October 20, 2025, stop with code 2587 \"Ul. Amsterdam\" for tram line No. 23 on Copenhagen Blvd. after Amsterdam Str. in direction of Obikolna Str. is temporarily closed.</span></p>",
                        "language": "en"
                        }
                    ]
                }
            }
        }
    
    expected = {
        "id": "fee63522-e3d5-4bdd-b6b7-92365577e84f",
        "alert": {
            "active_period": [
                {
                    "start": "1760313600",
                    "end": "1768203600"
                    }
                ],
            "informed_entity": [
                {
                    "route_id": "TM50"
                    }
                ],
            "cause": "OTHER_CAUSE",
            "effect": "STOP_MOVED",
            "url": {
                "translation": [
                    {
                        "text": "https://sofiatraffic.bg/bg",
                        "language": "bg"
                        },
                    {
                        "text": "https://sofiatraffic.bg/en",
                        "language": "en"
                        }
                    ]
                },
            "header_text": {
                "translation": [
                    {
                        "text": "",
                        "language": "bg"
                        },
                    {
                        "text": "",
                        "language": "en"
                        }
                    ]
                },
            "description_text": {
                "translation": [
                    {
                        "text": "<p>От 17:00 часа на 13.10.2025 г. спирка с код 2587 „Ул. Амстердам“ за трамвайна линия № 23 на бул. „Копенхаген“ след ул. Амстердам“ в посока ул. „Обиколна“ временно се закрива.</p>",
                        "language": "bg"
                        },
                    {
                        "text": "<p><span>From 17:00 on October 13, 2025 to October 20, 2025, stop with code 2587 \"Ul. Amsterdam\" for tram line No. 23 on Copenhagen Blvd. after Amsterdam Str. in direction of Obikolna Str. is temporarily closed.</span></p>",
                        "language": "en"
                        }
                    ]
                }
            }
        }
    
    result = normalize_keys_to_snake_case(entity)
    
    assert result == expected