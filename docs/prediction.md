![main](../img/header.png)


<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue?style=flat&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/macOS%20%7C%20Linux%20%7C%20Windows-supported-success?style=flat&colorA=2d2d2d&colorB=4a4a4a" alt="OS Supported" />
</p>

<p align="center">
  <img src="https://github.com/CoffeeIsAllYouNeed/Invisible-Driver/actions/workflows/python-package-conda.yml/badge.svg" alt="Python Package using Conda Status" />
  <img src="https://img.shields.io/badge/Pipeline_Tests-Passing-brightgreen?style=flat&logo=pytest" alt="Pipeline Tests Passing" />
  <img src="./coverage.svg" alt="Code Coverage" />
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/CoffeeIsAllYouNeed/Invisible-Driver?style=flat&logo=github&color=005571" alt="GitHub Stars" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" alt="License MIT" />
  <img src="https://img.shields.io/badge/Docs-Available-brightgreen?style=flat" alt="Docs Available" />
</p>

<p align="center">
<em>Brain Computer Interface to drive video game cars with EEG signals.</em>
</p>

## Model Training: 

* For **Model selection**, we tested unsupervised learning methods like KMeans, Gaussian Mixture Model, Agglomerative clustering, DBSCAN.Out of which **DBSCAN** performed highest with **Silhouette Coefficient of 0.53**.<br>
* Scaler used: Standard scalar.<br>
* Tuned parameters : {"EPS": 4.494850, "MIN_SAMPLES": 6, "METRIC": "euclidean"}<br> 
* The signal records will be classified into 2 states: **Beta, Gamma:** Attentive State & **Alpha:** Relaxed State
