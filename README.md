# System for Semantic Interoperability of Urban Data

The **System for Semantic Interoperability of Urban Data** is designed to collect and harmonize various types of urban data for the city of Sofia, Bulgaria, enabling smarter, data-driven decision-making. 

The backbone of the system is **FIWARE Orion-LD**, which ensures semantic interoperability and real-time context management.

## Data sources and formats

The system is design to have as input **heterogeneous urban data** from various sources, both static and realtime. Each data source is carefully transformed and semantically annotated to **ensure interoperability and compliance with NGSI-LD, a standard used by the FIWARE ecosystem.** 

Where official FIWARE data models or contexts are missing, we define **custom data models and @context files** to bridge the gap and provide semantic clarity in the transformation from raw formats to NGSI-LD.

Currently, the system integrates the following type of data:

### GTFS Static
* **Format:** ZIP archive containing standardized files in **CSV format**
* Represents scheduled transit information, including routes, timetables stop locations and more

### GTFS Realtime
* **Format:** Protocol Buffers (.pb), parsed using the official GTFS Realtime specification.

* Provides live transit updates, including:

    * `TripUpdate:` delays and early arrivals

    * `VehiclePosition:` real-time vehicle tracking

    * `Alert:` service disruptions and detours
