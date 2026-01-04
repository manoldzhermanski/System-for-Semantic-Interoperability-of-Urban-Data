from unittest.mock import patch
from orion_ld.orion_ld_crud_operations import orion_ld_batch_load_to_context_broker

def test_batch_load_sends_multiple_batches():
    """
    Check that if the entities are greater than the batch size, multiple function calls will be made
    """
    # Create 5 entities with batch size of 2
    ngsi_ld_data = [
        {"id": f"urn:ngsi-ld:Test:{i}", "type": "Test"} for i in range(5)
    ]
    
    # Define header
    headers = {"Content-Type": "application/ld+json"}

    # Patch helper function and time.sleep
    with patch("orion_ld.orion_ld_crud_operations.orion_ld_post_batch_request") as mock_post, \
        patch("orion_ld.orion_ld_crud_operations.time.sleep"):
        orion_ld_batch_load_to_context_broker(ngsi_ld_data, headers, batch_size=2, delay=0.01)

        # Check for 3 function calls
        assert mock_post.call_count == 3