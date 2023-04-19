# New-novelty-indicator-using-graph-theory-framework

This repository host codes from the paper XXX (Pelletier and Wirtz, 2023).

## Aim of the paper
The aim of our study was to gain insights on the team composition that supports successful novelty. To do this, we developed a measure that allowed us to identify the characteristics of researchers and examine the team composition that foster potential breakthrough novelty. Our analysis was based on the Pubmed Knowledge Graph, a digital library of scientific publications in health science. We investigated the relationship between our measure and expert perceptions of novelty (From Faculty Opinion), combinatorial novelty, and impact measures. Our findings suggest that teams with a highly diverse background fosters combinatorial novelty but that the relation follows an inverse u-shape. Furthermore a mix of highly exploratory and highly exploitative individuals are more likely to produce breakthrough novelty. Our study highlights the importance of team composition in facilitating successful novelty in scientific research. By identifying the factors that contribute to breakthroughs, we can better support research proposal with potential to advance the boundary of science but also create environments that facilitates the collaboration between exploratory and exploitative authors.

- This module uses mongoDB, make sure you have installed it before starting and have integrated the data. Neo4J will also be used, check that it is installed.

- The repository is structured as follow:

```bash
└── Paper
    ├── Data
    │    ├── Scimago_j_list
    │    └── Wos_j_list
    ├── Notebooks
    └── Results
        └── models
```

- All function used in the paper are store in the package folder. In order to run the analysis made in the paper, please follow the notebooks in the Notebooks folder. They are numbered in order of execution.

- If  you want to use the package for your own projects, follow the small tutorial below:

