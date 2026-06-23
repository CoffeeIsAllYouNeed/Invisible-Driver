![main](../img/header.png)


<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue?style=flat&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/macOS%20%7C%20Linux%20%7C%20Windows-supported-success?style=flat&colorA=2d2d2d&colorB=4a4a4a" alt="OS Supported" />
</p>

<p align="center">
  <img src="https://github.com/CoffeeIsAllYouNeed/Invisible-Driver/actions/workflows/python-package-conda.yml/badge.svg" alt="Python Package using Conda Status" />
  <img src="https://img.shields.io/badge/Pipeline_Tests-Passing-brightgreen?style=flat&logo=pytest" alt="Pipeline Tests Passing" />
  <img src="../coverage.svg" alt="Code Coverage" />
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/CoffeeIsAllYouNeed/Invisible-Driver?style=flat&logo=github&color=005571" alt="GitHub Stars" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" alt="License MIT" />
  <img src="https://img.shields.io/badge/Docs-Available-brightgreen?style=flat" alt="Docs Available" />
</p>

<p align="center">
<em>Brain Computer Interface to drive video game cars with EEG signals.</em>
</p>

## Results: 

<div align="center">

| Metric | Score |
| :---: | :---: |
| **Silhouette Coefficient (↑)** | `0.916` |
| **Davies-Bouldin Index (↓)** | `0.114` |
| **Calinski-Harabasz Score (↑)** | `1210.847` |

</div>



## Silhouette Coefficient: 

The Silhouette Score is a metric used to evaluate the quality of clustering in machine learning by measuring how close each data point in a cluster is to the data points in its neighboring clusters. It ranges from -1 to +1, where a higher score indicates better-defined and well-separated clusters.[[1]](#ref-1)

$$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$$



## Davies-Bouldin Index

The Davies-Bouldin Index evaluates clustering models by calculating the similarity between each cluster and its most similar peer. A lower score indicates better clustering, where clusters are tight and well-separated.[[2]](#ref-2)

$$R_{ij} = \frac{s_i + s_j}{d(c_i, c_j)}$$

$$DB = \frac{1}{k} \sum_{i=1}^{k} \max_{j \neq i} (R_{ij})$$



## Calinski-Harabasz Score

The Calinski-Harabasz Score, also known as the Variance Ratio Criterion, evaluates clustering models by calculating the ratio of the sum of between-cluster dispersion to within-cluster dispersion. A higher score indicates better-defined, tighter, and more separated clusters.[[3]](#ref-3)

$$CH = \frac{\text{Tr}(B_k)}{\text{Tr}(W_k)} \times \frac{n - k}{k - 1}$$



## References: 

<a id="ref-1"></a>

[1] [1] "What is Silhouette Score in Clustering?," GeeksforGeeks, Oct. 25, 2024. [Online]. Available: https://www.geeksforgeeks.org/machine-learning/what-is-silhouette-score/.

<a id="ref-2"></a>

[2] "Davies-Bouldin Index for Clustering Evaluation," GeeksforGeeks, Mar. 28, 2024. [Online]. Available: https://www.geeksforgeeks.org/machine-learning/davies-bouldin-index/.

<a id="ref-3"></a>

[3] "Calinski-Harabasz Index | Cluster Validity Indices Set-3," GeeksforGeeks, Aug. 14, 2024. [Online]. Available: https://www.geeksforgeeks.org/machine-learning/calinski-harabasz-index-cluster-validity-indices-set-3/.