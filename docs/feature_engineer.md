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

### Feature Engineering: 

* Alpha, Beta, Gamma waves are identified by the nature of their wave fluctuation.[[1]](#ref-1) Hence, this hints a vital point for new features.<br>
* Variance measures the dispersion of signal data points around their mean across designated time windows, which is engineered by calculating standard deviations globally over the full 2-second block as well as averaging smaller 1-second and 0.5-second sub-intervals.<br>
* Zero-Crossing Rate(ZCR) calculates the frequency at which the mean-centered signal switches sign to indicate oscillation velocity, which is engineered by measuring sign changes across both the total 2-second duration and segmented 1-second and 0.5-second time windows.<br>

### References: 

<a id="ref-1"></a>

[1] ScienceDirect Topics, "Brain Waves," *ScienceDirect*, [Online]. Available: [https://www.sciencedirect.com/topics/agricultural-and-biological-sciences/brain-waves](https://www.sciencedirect.com/topics/agricultural-and-biological-sciences/brain-waves).