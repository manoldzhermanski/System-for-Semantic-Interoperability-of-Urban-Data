import pytest
from gtfs_static.gtfs_static_utils import gtfs_static_fare_attributes_to_ngsi_ld

def test_valid_gtfs_agency_conversion():
    """
    Check that if all fields of GTFS Agency are provided,
    the entity is transfromed correctly into the NGSI-LD format
    """
    # Provide raw data
    raw_data = [
        {
            "fare_id": "A10",
            "price": "1.50",
            "currency_type": "BGN",
            "payment_method": "0",
            "transfers": "1",
            "agency_id": "A",
            "transfer_duration": "60"
        }
    ]
    
    # Provide expected result
    expected = [
        {
            "id": f"urn:ngsi-ld:GtfsFareAttributes:A10",
            "type": "GtfsFareAttributes",
            
            "price": {
                "type": "Property", 
                "value": 1.50
            },
            
            "currency_type": {
                "type": "Property", 
                "value": "BGN"
            },
            
            "payment_method": {
                "type": "Property", 
                "value": 0
            },
            
            "transfers": {
                "type": "Property", 
                "value": 1
            },
            
            "agency": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsAgency:A"
            },
            
            "transfer_duration": {
                "type" : "Property",
                "value": 60
            }
        }
    ]
    
    # Get result of the function call with the raw data
    result = gtfs_static_fare_attributes_to_ngsi_ld(raw_data)
    
    # Check that the result is as expected
    assert result == expected
    
def test_missing_fare_id_raises_value_error():
    """
    Check that if the 'fare_id' field is missing, a ValueError is raised
    """
    # Provide all required fields without 'fare_id'
    raw_data = [
        {
            "price": "1.50",
            "currency_type": "BGN",
            "payment_method": "0",
            "transfers": "1",
            "agency_id": "A",
        }
    ]
    
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_fare_attributes_to_ngsi_ld(raw_data)
        
def test_missing_fare_attributes_price_raises_value_error():
    """
    Check that if the 'price' field is missing, a ValueError is raised
    """
    # Provide all required fields without 'price'
    raw_data = [
        {
            "fare_id": "A10",
            "currency_type": "BGN",
            "payment_method": "0",
            "transfers": "1",
            "agency_id": "A"
        }
    ]
    
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_fare_attributes_to_ngsi_ld(raw_data)
        
def test_fare_attributes_negative_price_raises_value_error():
    """
    Check that if the 'price' field is negative, a ValueError is raised
    """
    # Provide a negative value for the 'price' field
    raw_data = [
        {
            "fare_id": "A10",
            "price": "-2.50",
            "currency_type": "BGN",
            "payment_method": "0",
            "transfers": "1",
            "agency_id": "A"
        }
    ]
    
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_fare_attributes_to_ngsi_ld(raw_data)
        
def test_missing_fare_attributes_currency_type_raises_value_error():
    """
    Check that if the 'currency_type' field is missing, a ValueError is raised
    """
    # Provide all required fields without 'currency_type'
    raw_data = [
        {
            "fare_id": "A10",
            "price": "1.50",
            "payment_method": "0",
            "transfers": "1",
            "agency_id": "A"
        }
    ]
    
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_fare_attributes_to_ngsi_ld(raw_data)

def test_missing_fare_attributes_payment_method_raises_value_error():
    """
    Check that if the 'payment_method' field is missing, a ValueError is raised
    """
    # Provide all required fields without 'payment_method'
    raw_data = [
        {
            "fare_id": "A10",
            "price": "1.50",
            "currency_type": "BGN",
            "transfers": "1",
            "agency_id": "A"
        }
    ]
    
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_fare_attributes_to_ngsi_ld(raw_data)

def test_fare_attributes_payment_method_invalid_value_raises_value_error():
    """
    Check that if the 'payment_method' field has an invalid value, a ValueError is raised
    """
    # Provide an invalid value for the 'payment_method' field
    raw_data = [
        {
            "fare_id": "A10",
            "price": "1.50",
            "currency_type": "BGN",
            "payment_method": "3",
            "transfers": "1",
            "agency_id": "A"
        }
    ]
    
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_fare_attributes_to_ngsi_ld(raw_data)
        
def test_missing_fare_attrubtes_transfers_raises_value_error():
    """
    Check that if the 'transfers' field is missing, a ValueError is raised
    """
    # Provide all required fields without 'transfers'
    raw_data = [
        {
            "fare_id": "A10",
            "price": "1.50",
            "currency_type": "BGN",
            "payment_method": "0",
            "agency_id": "A"
        }
    ]
    
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_fare_attributes_to_ngsi_ld(raw_data)

def test_fare_attributes_transfers_invalid_value_raises_value_error():
    """
    Check that if the 'transfers' field has an invalid value, a ValueError is raised
    """
    # Provide an invalid value for the 'transfers' field
    raw_data = [
        {
            "fare_id": "A10",
            "price": "1.50",
            "currency_type": "BGN",
            "payment_method": "0",
            "transfers": "3",
            "agency_id": "A"
        }
    ]
    
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_fare_attributes_to_ngsi_ld(raw_data)

def test_missing_fare_attributes_agency_id_raises_value_error():
    """
    Check that if the 'agency_id' field is missing, a ValueError is raised
    """
    # Provide all required fields without 'agency_id'
    raw_data = [
        {
            "fare_id": "A10",
            "price": "1.50",
            "currency_type": "BGN",
            "payment_method": "0",
            "transfers": "1"
        }
    ]
    
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_fare_attributes_to_ngsi_ld(raw_data)

def test_fare_attributes_negative_transfer_duration_raises_value_error():
    """
    Check that if the 'transfer_duration' field is negative, a ValueError is raised
    """
    # Provide a negative value for the 'transfer_duration' field
    raw_data = [
        {
            "fare_id": "A10",
            "price": "-2.50",
            "currency_type": "BGN",
            "payment_method": "0",
            "transfers": "1",
            "agency_id": "A",
            "transfer_duration": "-1"
        }
    ]
    
    # Check that a ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_fare_attributes_to_ngsi_ld(raw_data)

def test_optinal_fields_are_removed_if_empty():
    """
    Check that if the an optional field is empty, that field will be removed
    """
    # Provide all required fields with an empty optional field
    raw_data = [
        {
            "fare_id": "A10",
            "price": "1.50",
            "currency_type": "BGN",
            "payment_method": "0",
            "transfers": "1",
            "agency_id": "A",
            "transfer_duration": ""
        }
    ]
    
    # Provide expected result
    expected = [
{
            "id": f"urn:ngsi-ld:GtfsFareAttributes:A10",
            "type": "GtfsFareAttributes",
            
            "price": {
                "type": "Property", 
                "value": 1.50
            },
            
            "currency_type": {
                "type": "Property", 
                "value": "BGN"
            },
            
            "payment_method": {
                "type": "Property", 
                "value": 0
            },
            
            "transfers": {
                "type": "Property", 
                "value": 1
            },
            
            "agency": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsAgency:A"
            }
        }
    ]
    
    # Get result of the function call with the raw data
    result = gtfs_static_fare_attributes_to_ngsi_ld(raw_data)
    
    # Check that the result is as expected
    assert result == expected

def test_multiple_entities():
    """
    Check if the raw data contains 2 entities, 
    after the transformation 2 entites are returned from the function call
    """
    # Provide 2 entities
    raw_data = [
        {
            "fare_id": "A10",
            "price": "1.50",
            "currency_type": "BGN",
            "payment_method": "0",
            "transfers": "1",
            "agency_id": "A",
            "transfer_duration": "60"
        },
        {
            "fare_id": "A11",
            "price": "1.60",
            "currency_type": "BGN",
            "payment_method": "0",
            "transfers": "1",
            "agency_id": "A",
            "transfer_duration": "30"
        }
    ]
    
    # Get result from the function call
    result = gtfs_static_fare_attributes_to_ngsi_ld(raw_data)
    
    # Check if 2 entities are returned after the function call
    assert len(result) == 2

def test_unknown_fields_are_ignored():
    """
    Check if an unknown data field is provided,
    it's ignored during the transformation
    """
    # Provide data with unknown field
    raw_data = [
        {
            "fare_id": "A10",
            "price": "1.50",
            "currency_type": "BGN",
            "payment_method": "0",
            "transfers": "1",
            "agency_id": "A",
            "transfer_duration": "60",
            "unkown_field": "unknown_value"
        }
    ]
    
    # Provide expected result
    expected = [
        {
            "id": f"urn:ngsi-ld:GtfsFareAttributes:A10",
            "type": "GtfsFareAttributes",
            
            "price": {
                "type": "Property", 
                "value": 1.50
            },
            
            "currency_type": {
                "type": "Property", 
                "value": "BGN"
            },
            
            "payment_method": {
                "type": "Property", 
                "value": 0
            },
            
            "transfers": {
                "type": "Property", 
                "value": 1
            },
            
            "agency": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsAgency:A"
            },
            
            "transfer_duration": {
                "type": "Property",
                "value": 60
            }
        }
    ]
    
    result = gtfs_static_fare_attributes_to_ngsi_ld(raw_data)
    
    assert result == expected

def test_whitespace_values_are_removed():
    """
    Check that if the an optional field contains white space as a value, that field will be removed
    """
    # Provide all required fields with an optional field whith a white space as a value
    raw_data = [
        {
            "fare_id": "A10",
            "price": "1.50",
            "currency_type": "BGN",
            "payment_method": "0",
            "transfers": "1",
            "agency_id": "A",
            "transfer_duration": " "
        }
    ]
    
    # Provide expected result
    expected = [
        {
            "id": f"urn:ngsi-ld:GtfsFareAttributes:A10",
            "type": "GtfsFareAttributes",
            
            "price": {
                "type": "Property", 
                "value": 1.50
            },
            
            "currency_type": {
                "type": "Property", 
                "value": "BGN"
            },
            
            "payment_method": {
                "type": "Property", 
                "value": 0
            },
            
            "transfers": {
                "type": "Property", 
                "value": 1
            },
            
            "agency": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsAgency:A"
            }
        }
    ]
    
    # Get result of the function call with the raw data
    result = gtfs_static_fare_attributes_to_ngsi_ld(raw_data)
    
    # Check that the result is as expected
    assert result == expected
     
def test_empty_agency_dict_raises_error():
    """
    Check that if a list with empty entities are provided, a ValueError is raised
    """
    # Provide a list with empty entities
    raw_data = [{}, {}]
    
    # Check that ValueError is raised
    with pytest.raises(ValueError):
        gtfs_static_fare_attributes_to_ngsi_ld(raw_data)
        
def test_empty_raw_data_returns_empty_list():
    """
    If an empty list is provided, the function call should return an empty list
    """
    # Provide empty list
    raw_data = []
    
    # Check that the function call returns an empty list
    assert gtfs_static_fare_attributes_to_ngsi_ld(raw_data) == []