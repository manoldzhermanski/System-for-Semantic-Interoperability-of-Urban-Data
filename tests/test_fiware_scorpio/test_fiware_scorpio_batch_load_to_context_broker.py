from unittest.mock import patch
from fiware_scorpio.fiware_scorpio_crud_operations import fiware_scorpio_batch_load_to_context_broker

def test_batch_load_sends_multiple_batches():
    """
    Check that if the entities are greater than the batch size,
    multiple function calls will be made
    """

    # Create 5 entities
    ngsi_ld_data = [
        {"id": f"urn:ngsi-ld:Test:{i}", "type": "Test"} for i in range(5)
    ]

    # Simulate batching (batch size = 2)
    batches = [
        ngsi_ld_data[0:2],
        ngsi_ld_data[2:4],
        ngsi_ld_data[4:5],
    ]

    headers = {"Content-Type": "application/ld+json"}

    with patch("fiware_scorpio.fiware_scorpio_crud_operations.fiware_scorpio_post_batch_request") as mock_post, \
         patch("fiware_scorpio.fiware_scorpio_crud_operations.time.sleep"):

        fiware_scorpio_batch_load_to_context_broker(iter(batches), headers, delay=0.01)

        # Expect 3 calls (5 entities, batch size 2)
        assert mock_post.call_count == 3