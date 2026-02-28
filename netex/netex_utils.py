import sys
from typing import Iterator, Any
from pathlib import Path
from lxml import etree

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from gtfs_static.gtfs_static_utils import gtfs_static_get_ngsi_ld_batches

NS = "http://www.netex.org.uk/netex"
NSMAP = {None: NS}
    
def netex_transform_ngsi_ld_agency_to_operator(entities: Iterator[list[dict[str, Any]]]) -> str:
    """
    Transforms NGSI-LD GtfsAgency entities to NeTEx Operator XML nested in a ResourceFrame.

    Args:
        entities: List iterator of NGSI-LD GtfsAgency
                  Required fields:
                  - agency_name
                  - agency_url
                  - agency_phone
                  - agency_email
                  - id

    Returns:
        XML string with ResourceFrame and Operator objects
    """

    # PublicationDelivery
    pub = etree.Element("PublicationDelivery", nsmap=NSMAP)
    pub.set("version", "1.15:NO-NeTEx-networktimetable:1.5")

    # CompositeFrame
    comp_frame = etree.SubElement(pub, "CompositeFrame", id="CompositeFrame:1", version="1")

    # ResourceFrame
    res_frame = etree.SubElement(comp_frame, "ResourceFrame", id="ResourceFrame:1", version="1")

    # organisations container
    organisations = etree.SubElement(res_frame, "organisations")

    # обхождаме всички NGSI-LD ентитети
    for batch in entities:
        for entity in batch:
            
            id_value = entity.get("id")
    
            entity_id = id_value.split(":")[-1] if id_value else "unknown"
            city = id_value.split(":")[-2] if id_value else "unknown"
            name = entity.get("agency_name", {}).get("value")
            url = entity.get("agency_url", {}).get("value", "")
            phone = entity.get("agency_phone", {}).get("value", "")
            email = entity.get("agency_email", {}).get("value", "")

            operator = etree.SubElement(
                organisations,
                "Operator",
                version="1",
                id=f"{city}:Operator:{entity_id}"
            )

            # Name
            name_el = etree.SubElement(operator, "Name")
            name_el.text = name
            
            # Legal Name
            legal_name_el = etree.SubElement(operator, "LegalName")
            legal_name_el.text = name

            # ContactDetails
            contact = etree.SubElement(operator, "ContactDetails")
            if url:
                url_el = etree.SubElement(contact, "Url")
                url_el.text = url
            if phone:
                phone_el = etree.SubElement(contact, "Phone")
                phone_el.text = phone
            if email:
                email_el = etree.SubElement(contact, "Email")
                email_el.text = email

    return etree.tostring(pub, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode("utf-8")


def convert_ngsi_stop_to_nordic_netex(entity: dict) -> etree.Element:
    
    id_value = entity.get("id")
    
    stop_id = id_value.split(":")[-1] if id_value else "unknown"
    city = id_value.split(":")[-2] if id_value else "unknown"
    location_type = entity.get("locationType", {}).get("value", 0)

    name_value = entity.get("name", {}).get("value")
    code_value = entity.get("code", {}).get("value")

    coords = entity.get("location", {}).get("value", {}).get("coordinates")

    parent = entity.get("hasParentStation", {}).get("object")
    wheelchair = entity.get("wheelchair_boarding", {}).get("value")

    # --- CREATE STOPPLACE ---
    stopplace = etree.Element("StopPlace", nsmap=NSMAP)
    stopplace.set("id", f"{city}:StopPlace:{stop_id}")
    stopplace.set("version", "1")

    if name_value:
        name_el = etree.SubElement(stopplace, "Name")
        name_el.text = name_value

    # Parent reference
    if parent:
        parent_ref = etree.SubElement(stopplace, "ParentSiteRef")
        parent_ref.set("ref", f"{city}:StopPlace:{parent}")
        parent_ref.set("version", "1")

    # Coordinates
    if coords:
        centroid = etree.SubElement(stopplace, "Centroid")
        loc = etree.SubElement(centroid, "Location")
        etree.SubElement(loc, "Longitude").text = str(coords[0])
        etree.SubElement(loc, "Latitude").text = str(coords[1])

    # Accessibility
    if wheelchair is not None:
        access = etree.SubElement(stopplace, "AccessibilityAssessment")
        mobility = etree.SubElement(access, "MobilityImpairedAccess")

        if wheelchair == 1:
            mobility.text = "true"
        elif wheelchair == 2:
            mobility.text = "false"
        else:
            mobility.text = "unknown"

    # StopPlaceType (safe fallback for OTP)
    sptype = etree.SubElement(stopplace, "StopPlaceType")

    if location_type == 1:
        sptype.text = "station"
    else:
        sptype.text = "other"

    # --- CREATE QUAY FOR BOARDING POINTS ---
    if location_type in (0, 4):

        quays_container = etree.SubElement(stopplace, "quays")

        quay = etree.SubElement(quays_container, "Quay")
        quay.set("id", f"{city}:Quay:{stop_id}")
        quay.set("version", "1")

        if code_value:
            etree.SubElement(quay, "PublicCode").text = str(code_value)

        if coords:
            centroid = etree.SubElement(quay, "Centroid")
            loc = etree.SubElement(centroid, "Location")
            etree.SubElement(loc, "Longitude").text = str(coords[0])
            etree.SubElement(loc, "Latitude").text = str(coords[1])

    return stopplace
    
if __name__ == "__main__":
    for batch in gtfs_static_get_ngsi_ld_batches("stops", "Sofia"):
        for ngsi_entity in batch:
            xml_element = convert_ngsi_stop_to_nordic_netex(ngsi_entity)
            print(etree.tostring(xml_element, pretty_print=True, encoding="unicode"))