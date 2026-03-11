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

# TO-DO: DayTypeAssignment has to be contained in dayTypeAssignments
#        dayTypeAssignments has to be contained in ServiceCalendarFrame 
def netex_convert_calendar_dates_to_day_type_assignment(entity: dict[str, Any]):

    id_value = entity.get("id", None)
    
    city = id_value.split(":")[-3] if id_value else "Unknown"
    service_id = id_value.split(":")[-2] if id_value else "Unknown"
    date = id_value.split(":")[-1] if id_value else "Unknown"
    
    exception_type = entity.get("exceptionType", {}).get("value")
    is_available = exception_type == 1
    is_available_value = "true" if is_available else "false"

    day_type_assignment = etree.Element("DayTypeAssignment")
    day_type_assignment.set("id", f"{city}:DayTypeAssignment:{service_id}-{date}")
    day_type_assignment.set("version", "0")

    if service_id is not None:
        service = etree.SubElement(day_type_assignment, "DayTypeRef")
        service.set("ref", f"{city}:DayType:{service_id}")
        service.set("version", "0")

    if date is not None:
        service_date = etree.SubElement(day_type_assignment, "Date")
        service_date.text = date

    if exception_type is not None:
        is_available_xml = etree.SubElement(day_type_assignment, "isAvailable")
        is_available_xml.text = is_available_value

    return day_type_assignment

def netex_convert_routes_to_lines(entity: dict[str, Any]):
    id_value = entity.get("id")
    route_id = id_value.split(":")[-1] if id_value else "unknown"
    city = id_value.split(":")[-2] if id_value else "unknown"

    

    line = etree.Element("Line")
    line.set("id", f"{city}:Line:{route_id}")
    line.set("version", "0")

    route_long_name = entity.get("name", {}).get("value")
    if route_long_name:
        line_name = etree.SubElement(line, "Name")
        line_name.text = route_long_name

    route_description = entity.get("description", {}).get("value")
    if route_description:
        line_description = etree.SubElement(line, "Description")
        line_description.text = route_description

    # TO-DO: WRITE A FUNCTION FOR THE TransportMode AND TransportSubmode
    # REFERENCE: https://github.com/entur/netex-gtfs-converter-java

    route_url = entity.get("route_url", {}).get("value")
    if route_url:
        line_url = etree.SubElement(line, "Url")
        line_url.text = route_url

    route_short_name = entity.get("shortName", {}).get("value")
    if route_short_name:
        line_name = etree.SubElement(line, "PublicCode")
        line_name.text = route_short_name

    agency = entity.get("operatedBy", {}).get("object")
    if agency:
        agency_id = agency.split(":")[-1]
        line_operator_ref = etree.SubElement(line, "OperatorRef")
        line_operator_ref.set("ref", f"{city}:Operator:{agency_id}")

    route_colour = entity.get("routeColor", {}).get("value")
    route_text_colour = entity.get("routeTextColor", {}).get("value")
    if route_colour or route_text_colour:
        presentation = etree.SubElement(line, "Presentation")
        
        if route_colour:
            line_colour = etree.SubElement(presentation, "Colour")
            line_colour.text = route_colour

        if route_text_colour:
            line_text_colour = etree.SubElement(presentation, "TextColour")
            line_text_colour.text = route_text_colour

    return line
    
if __name__ == "__main__":
    for batch in gtfs_static_get_ngsi_ld_batches("routes", "Sofia"):
        for ngsi_entity in batch:
            xml_element = netex_convert_routes_to_lines(ngsi_entity)
            print(etree.tostring(xml_element, pretty_print=True, encoding="unicode"))