import sys
from typing import Iterator, Any
from pathlib import Path
from lxml import etree

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from gtfs_static.gtfs_static_utils import gtfs_static_get_ngsi_ld_batches

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
    NS = "http://www.netex.org.uk/netex"
    NSMAP = {None: NS}

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
            entity_id = entity.get("id").split(":")[-1]
            name = entity.get("agency_name", {}).get("value")
            url = entity.get("agency_url", {}).get("value", "")
            phone = entity.get("agency_phone", {}).get("value", "")
            email = entity.get("agency_email", {}).get("value", "")

            operator = etree.SubElement(
                organisations,
                "Operator",
                version="1",
                id=f"{entity_id}:Operator:{entity_id}"
            )

            # Name
            name_el = etree.SubElement(operator, "Name")
            name_el.text = name

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

if __name__ == "__main__":
    for batch in gtfs_static_get_ngsi_ld_batches("agency", "Sofia"):
        xml_output = netex_transform_ngsi_ld_agency_to_operator([batch])
        print(xml_output)