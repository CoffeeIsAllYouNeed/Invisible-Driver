![main](img/header.png)


<h1 align="center">Drive Car using Brain</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11-blue?style=flat&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" alt="License MIT" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Docs-Available-brightgreen?style=flat" alt="Docs Available" />
  <img src="https://img.shields.io/badge/Contributions-Welcome-blue?style=flat" alt="Contributions Welcome" />
</p>

<p align="center">
"Invisible Driver" is a BCI project, in which you can drive video-game cars using brain's EEG signals.
</p>

### Hardware:  

| Component | Image | Quantity |
| :--- | :---: | :---: |
| **BioAmp EXG Pill** *(with JST PH 2.0 connector and a header pin)* | <img src="https://5.imimg.com/data5/SELLER/Default/2025/3/496928027/TL/KJ/FM/156942136/bioamp-exg-pill-unassembled-record-publication-grade-ecg-emg-eog-or-eeg.jpg" alt="BioAmp EXG Pill" height="200"/> | 1 |
| **BioAmp Cable v3** | <img src="https://store.upsidedownlabs.tech/wp-content/uploads/2022/11/1-1.jpg" alt="BioAmp Cable v3" height="200"/> | 1 |
| **Gel Electrodes** | <img src="https://shop.openbci.com/cdn/shop/files/kendall-35mm.jpg?v=1694030384" alt="Gel Electrodes" height="200"/> | 3 |
| **Jumper Cables** | <img src="https://store.arduino.cc/cdn/shop/files/TPX00159_01.front_05719685-eb39-4977-8a01-1641461536c3_500x309.jpg?v=1771603575" alt="Jumper Cables" height="200"/> | 3 |
| **Arduino Uno** | <img src="https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2015/11/4-1.jpg" alt="Arduino Uno" height="200"/> | 1 |
| **Nuprep Skin Gel** | <img src="https://5.imimg.com/data5/SELLER/Default/2023/11/359233054/ZL/BR/TB/6317077/nuprep-skin-prep-gel.jpg" alt="Nuprep Gel" height="200"/> | 1 |
| **Wet wipe** | <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRsv88h91KOPFHaZ2LRVbLFBsSklgK8cKsKKw&s" alt="Wet Wipe" height="200"/> | 1 |
| **Brain BioAmp Band** *(Optional)* | <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTSStS1rGSGPOKB8LvksVjaPrnp_PpdSBoJcw&s" alt="Brain BioAmp Band" height="200"/> | 1 |
| **Electrode Gel** *(If using Brain BioAmp Band)* | <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS1vwdu5_kiqXnaBjBTfNPYy9Il8SrIOLQX5w&s" alt="Electrode Gel" height="200"/> | 1 |

---

### Software: 

* **Arduino IDE**
* **Visual Studio Code**
* **Google Colab**

---

### Hardware connection steps: 

#### Step 1: Assembly
If your BioAmp EXG Pill did not come pre-soldered, solder the header pins and the JST PH 2.0 connector onto the board.

<p align="center">
  <img src="img/assembly.jpeg" width="400" alt="Assembly Diagram" />
</p>

#### Step 2: Skin Preparation
Gently rub Nuprep Skin Preparation Gel onto your forehead and behind your earlobes to lower skin impedance and improve signal accuracy. Wipe the areas clean with a wet wipe.

<p align="center">
  <img src="img/skin_preparation.png" width="400" alt="Skin Preparation" />
</p>

#### Step 3: Connecting Electrode Cable
Plug the BioAmp Cable v3 directly into the JST PH 2.0 connector on the BioAmp EXG Pill.

<p align="center">
  <img src="img/connect_electrodes.png" width="400" alt="Cable Connection" />
</p>

#### Step 4: Electrode Placement
Snap the cable onto 3 gel electrodes and peel off their plastic backings. Place the **IN+** electrode on your forehead (between Fp1 and Fp2 positions). Place the **IN-** and **REF** electrodes on the bony areas behind your earlobes.

<p align="center">
  <img src="img/electrode_placement.png" width="400" alt="Electrode Placement Diagram" />
</p>

#### Step 5: Connect Development Board
Use jumper cables to connect the BioAmp EXG Pill to your Arduino Uno / Maker Uno. 

**CRITICAL:** Double-check your VCC and GND connections. Reversing them can permanently damage your sensor.

* **VCC** = **5V**
* **GND** = **GND**
* **OUT** = **A0**

<p align="center">
  <img src="img/connect_development_ board.png" width="400" alt="Wiring Diagram" />
</p>

---

### Software connection steps: 

#### Step 1: Clone the Repository

```bash
git clone https://github.com/CoffeeIsAllYouNeed/Invisible-Driver 
cd Invisible-Driver

```

#### Step 2: Install dependencies

```bash
pip install -r requirements.txt

```

#### Step 3: Flash Hardware

1. Connect EEG hardware module to computer via USB.
2. Open the file located at `hardware/eeg.ino` using the Arduino IDE.
3. Select board type and active communication port.
4. Click **Upload** to flash the code into the hardware.

#### Step 4: Run the following command in terminal

```bash
uvicorn server:app --reload --port 8000

```

#### Step 5: Navigate to the Game Platform to Drive with Brain

Navigate: **`http://127.0.0.1:8000`**

---

### Directory structure: 

```text
Invisible-Driver/
├── data/                    # Stores sample data & live data.
│   ├── data.csv             # Sample 5 min data for simulation.
│   └── signal.parquet       # Live data.
├── docs/                    # documentation.
│   ├── eeg.md               # documentation for EEG signal processing.
│   ├── feature_engineer.md  # documentation for feature engineering.
│   ├── hardware.md          # documentation for hardware setup and microcontrollers.
│   ├── ingestion.md         # documentation for data ingestion.
│   ├── pipeline.md          # documentation for the overall system pipeline.
│   ├── predict.md           # documentation for model training.
│   ├── preprocess.md        # documentation for data preprocessing.
│   ├── reproducible.md      # documentation for reproducible results.
│   └── UPDATES.md           # Updates documentation.
├── hardware/                # hardware scripts.
│   └── eeg.ino              # Arduino C++ sketch for live EEG data fetch.
├── model/                   # Stores pre-trained models.
│   └── model.pkl            # Pre-trained unsupervised model.
├── src/                     # Pipeline modules.
│   ├── __init__.py
│   ├── feature_engineer.py  # Pipeline step: Feature engineering.
│   ├── ingest.py            # Pipeline step: Data ingestion.
│   ├── prediction.py        # Pipeline step: Model training.
│   ├── preprocess.py        # Pipeline step: Data preprocessing.
│   └── reproducible.py      # Pipeline step: Reproducibility.
├── templates/
│   └── ui.html              # Racing car UI
├── .gitignore
├── LICENSE                  # Open-source MIT distribution terms
├── prediction.ipynb         # Unsupervised model.
├── README.md                # Project overview.
├── requirements.txt         # Dependencies.
├── run.py                   # Pipeline run file.
├── server.py                # FastAPI server.
```
---

### Wanna Chat?: 

* [My LinkedIn](https://www.linkedin.com/in/vrushal-more-2a5067330?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app)
