![main](../img/header.png)


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

### Model Training: 

* For **Model selection**, we tested unsupervised learning methods like KMeans, Gaussian Mixture Model, Agglomerative clustering, DBSCAN.Out of which **DBSCAN** performed highest with **Silhouette Coefficient of 0.53**.<br>
* Scaler used: Standard scalar.<br>
* Tuned parameters : {"EPS": 4.494850, "MIN_SAMPLES": 6, "METRIC": "euclidean"}<br> 
* The signal records will be classified into 2 states: **Beta, Gamma:** Attentive State & **Alpha:** Relaxed State
