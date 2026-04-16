import pytest
from netex.netex_utils import netex_helper_get_transport_mode_and_submode

@pytest.mark.parametrize(
    "gtfs_code, expected",
    [
        (-1, (None, None)),
        (99, (None, None)),
        (100, ('rail', 'unknown')),
        (101, ('rail', 'airportLinkRail')),
        (102, ('rail', 'longDistance')),
        (103, ('rail', 'interregionalRail')),
        (105, ('rail', 'nightRail')),
        (106, ('rail', 'regionalRail')),
        (107, ('rail', 'touristRailway')),
        (108, ('rail', 'airportLinkRail')),
        (109, ('rail', 'regionalRail')),
        (200, ('coach', 'unknown')),
        (201, ('coach', 'internationalCoach')),
        (202, ('coach', 'nationalCoach')),
        (204, ('coach', 'touristCoach')),
        (400, ('metro', 'urbanRailway')),
        (401, ('metro', 'metro')),
        (402, ('metro', 'metro')),
        (403, ('metro', 'urbanRailway')),
        (405, ('metro', 'urbanRailway')),
        (700, ('bus', 'unknown')),
        (701, ('bus', 'regionalBus')),
        (702, ('bus', 'expressBus')),
        (704, ('bus', 'localBus')),
        (715, ('bus', 'unknown')),
        (800, ('trolleyBus', 'unknown')),
        (900, ('tram', 'unknown')),
        (1000, ('water', 'unknown')),
        (1200, ('water', 'unknown')),
        (1300, ('cableway', 'unknown')),
        (1301, ('cableway', 'telecabin')),
        (1400, ('funicular', 'funicular')),
        (1501, ('taxi', 'communalTaxi')),
        (1700, ('other', 'unknown')),
        (1702, ('other', 'unknown'))
    ],
)
def test_mapping(gtfs_code, expected):
    assert netex_helper_get_transport_mode_and_submode(gtfs_code) == expected