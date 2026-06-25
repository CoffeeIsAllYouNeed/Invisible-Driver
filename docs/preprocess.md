![main](../img/header_1.png)


<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue?style=flat&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/macOS%20%7C%20Linux%20%7C%20Windows-supported-success?style=flat&colorA=2d2d2d&colorB=4a4a4a" alt="OS Supported" />
</p>

<p align="center">
  <img src="https://github.com/CoffeeIsAllYouNeed/Invisible-Driver/actions/workflows/python-package-conda.yml/badge.svg" alt="Python Package using Conda Status" />
  <img src="https://img.shields.io/badge/Pipeline_Tests-Passing-brightgreen?style=flat&logo=pytest" alt="Pipeline Tests Passing" />
  <img src="../img/coverage.svg" alt="Code Coverage" />
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/CoffeeIsAllYouNeed/Invisible-Driver?style=flat&logo=github&color=005571" alt="GitHub Stars" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" alt="License MIT" />
  <img src="https://img.shields.io/badge/Docs-Available-brightgreen?style=flat" alt="Docs Available" />
</p>

<p align="center">
<em>Brain Computer Interface to drive video game cars with EEG signals.</em>
</p>

## Data Preprocess: 

* As per research, 2 seconds Time-Window is ideal for emotion recognition.[[1]](#ref-1) Hence, data is collected continuosly for 2 seconds interval and then further predictions are done.<br>
* Each record of 2s-TW will consists multiple signal values. This will be helpful to understand the pattern of wave fluctuation and classify waves as:  Alpha, Beta, Gammma.[[2]](#ref-2)<br>
<p align="center">
  <img src="https://ars.els-cdn.com/content/image/3-s2.0-B9780128044902000026-f02-01-9780128044902.jpg" width="400" alt="Types of waves"/>
  <br>
  <em>Figure 1: Types of brain-waves</em>
</p>

* For sorting, Quick Sort is implemented as it has low time complexity[Avg. Time Complexity: *O(nlogn)*] and Space Complexity[*O(logn)*].[[3]](#ref-3)<br>



## References: 

<a id="ref-1"></a>

[1] D. Ouyang, Y. Yuan, G. Li, and Z. Guo, "The Effect of Time Window Length on EEG-Based Emotion Recognition," *Sensors*, vol. 22, no. 13, p. 4939, Jun. 2022. [Online]. Available: [https://pmc.ncbi.nlm.nih.gov/articles/PMC9269830/](https://pmc.ncbi.nlm.nih.gov/articles/PMC9269830/).

<a id="ref-2"></a>

[2] ScienceDirect Topics, "Brain Waves," *ScienceDirect*, [Online]. Available: [https://www.sciencedirect.com/topics/agricultural-and-biological-sciences/brain-waves](https://www.sciencedirect.com/topics/agricultural-and-biological-sciences/brain-waves).

<a id="ref-3"></a>

[3] Programiz Pro, "Quick Sort Complexity," *Programiz Pro Resources*, [Online]. Available: [https://programiz.pro/resources/dsa-quick-sort-complexity/](https://programiz.pro/resources/dsa-quick-sort-complexity/).