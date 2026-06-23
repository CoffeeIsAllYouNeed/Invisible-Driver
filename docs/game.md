![main](../img/header.png)


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

## Why car game? 

As per research, 2 seconds Time-Window is ideal for emotion recognition.[[1]](#ref-1) Hence, data is collected continuosly for 2 seconds interval and then state predictions are done. Games like flappy bird, dino jump require smaller reaction interval. Thus they aren't suitable for BCI game. Hence, the car game where the reaction time is much higher. 



## How to play? 

* User can setup the hardware & Invisible driver repository to play the game.
* In absence of hardware one can simulate with the available data in repository.
* Also, user can observe the predicted cognitive state, throttle mode, and eeg readings on the game platform and on EEG graph.

<p align="center">
  <img src="../img/game.png" width="800" alt="Game"/>
  <br>
  <em>Figure 1: Game</em>
</p>



## References: 

<a id="ref-1"></a>

[1] D. Ouyang, Y. Yuan, G. Li, and Z. Guo, "The Effect of Time Window Length on EEG-Based Emotion Recognition," *Sensors*, vol. 22, no. 13, p. 4939, Jun. 2022. [Online]. Available: [https://pmc.ncbi.nlm.nih.gov/articles/PMC9269830/](https://pmc.ncbi.nlm.nih.gov/articles/PMC9269830/).
