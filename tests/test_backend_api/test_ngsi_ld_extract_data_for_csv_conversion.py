from backend_api.main import ngsi_ld_extract_data_for_csv_conversion

def test_ngsi_ld_extract_data_for_csv_conversion_fare_attributes():
  
    raw_data = {
    "id": "urn:ngsi-ld:GtfsFareAttributes:Sofia:A60",
    "type": "GtfsFareAttributes",
    "price": {
      "type": "Property",
      "value": 1.1
    },
    "currency_type": {
      "type": "Property",
      "value": "EUR"
    },
    "payment_method": {
      "type": "Property",
      "value": 1
    },
    "transfers": {
      "type": "Property",
      "value": -1
    },
    "agency": {
      "type": "Relationship",
      "object": "urn:ngsi-ld:GtfsAgency:Sofia:A"
    },
    "transfer_duration": {
      "type": "Property",
      "value": 3600
    }
  }
    
    expected = [
      {
        "fare_id": "A60",
        "price": 1.1,
        "currency_type": "EUR",
        "payment_method": 1,
        "transfers": -1,
        "agency_id": "A",
        "transfer_duration": 3600
        }
      ]
    
    result = ngsi_ld_extract_data_for_csv_conversion(raw_data)

    assert result == expected