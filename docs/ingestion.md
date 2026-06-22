![main](../img/header.png)


<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue?style=flat&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/macOS%20%7C%20Linux%20%7C%20Windows-supported-success?style=flat&colorA=2d2d2d&colorB=4a4a4a" alt="OS Supported" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" alt="License MIT" />
  <img src="https://img.shields.io/badge/Docs-Available-brightgreen?style=flat" alt="Docs Available" />
</p>

<p align="center">
Brain Computer Interface to drive video game cars with EEG signals. 
</p>

## Data Ingestion: 

* Data Ingestion is responsible for fetching the data from hardware BCI setup.<br>
* When hardware available: It stores the data in parquet format for memory efficiency.<br>
* When hardware absent: It has pre-stored data in CSV format to run simulation.<br>
* Modern Arduino's bootloader normally finishes initializing in 1 to 2 seconds, a 5-second delay is implemented as a safety margin to guarantee a stable connection. [[1]](#ref-1)<br>
* Older Arduino's bootloader might take around 4 to 8 seconds to initialize. Extend the sleep time to 10 seconds in that case. [[1]](#ref-1)<br>
* Date-Time format used: %Y-%m-%d %H:%M:%S.%f.<br>
* The bad value handling is skipped as they are dealt in preprocessing step.<br>
* For faster processing and efficient memory usage we used C engine in CSV handling to enable low memory option & converted all values to int32.



## References: 

<a id="ref-1"></a>

[1] Optiboot contributors, "optiboot.c," *GitHub Repository: Optiboot/optiboot*, [Online]. Available: [https://github.com/Optiboot/optiboot/blob/master/optiboot/bootloaders/optiboot/optiboot.c](https://github.com/Optiboot/optiboot/blob/master/optiboot/bootloaders/optiboot/optiboot.c).<br>