import pytest
import asyncio
from unittest.mock import patch, MagicMock

from backend_api.main import update_vehicle_positions_loop

@pytest.mark.asyncio
async def test_update_vehicle_positions_loop_happy_path():
    mock_ngsi_entities = [{"id": "1"}]
    mock_orion_entities = [{"id": "veh1"}]
    mock_feed = MagicMock()
    mock_feed.entity = [1, 2, 3]

    with (
        patch("backend_api.main.gtfs_realtime_get_ngsi_ld_data", return_value=mock_ngsi_entities) as mock_get_ngsi,
        patch("backend_api.main.orion_ld_define_header", return_value={"header": "x"}) as mock_header,
        patch("backend_api.main.orion_ld_batch_replace_entity_data") as mock_batch,
        patch("backend_api.main.orion_ld_get_entities_by_type", return_value=mock_orion_entities) as mock_get_entities,
        patch("backend_api.main.ngsi_ld_vehicle_positions_to_feed_message", return_value=mock_feed) as mock_build_feed,
        patch("backend_api.main.asyncio.sleep", side_effect=asyncio.CancelledError),
        patch("backend_api.main.logger") as mock_logger,
    ):
        # Act: loop runs once, then CancelledError stops it
        with pytest.raises(asyncio.CancelledError):
            await update_vehicle_positions_loop()

        # Assert call sequence / behavior
        mock_get_ngsi.assert_called_once_with("VehiclePosition")
        mock_header.assert_called_once_with("gtfs_realtime")
        mock_batch.assert_called_once_with(mock_ngsi_entities, {"header": "x"})
        mock_get_entities.assert_called_once_with(
            "GtfsRealtimeVehiclePosition",
            {"header": "x"}
        )
        mock_build_feed.assert_called_once_with(mock_orion_entities)

        mock_logger.info.assert_called_once_with(
            "GTFS feed built: entities=%d",
            len(mock_feed.entity)
        )

@pytest.mark.asyncio
async def test_update_vehicle_positions_loop_exception_logged():
    with (
        patch("backend_api.main.gtfs_realtime_get_ngsi_ld_data", side_effect=RuntimeError()),
        patch("backend_api.main.asyncio.sleep", side_effect=asyncio.CancelledError),
        patch("backend_api.main.logger") as mock_logger,
    ):
        with pytest.raises(asyncio.CancelledError):
            await update_vehicle_positions_loop()

        mock_logger.exception.assert_called_once()
