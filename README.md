# New-novelty-indicator-using-graph-theory-framework

- This repository host codes from the paper XXX (Pelletier and Wirtz, 2021 (On y croit !)), in this paper we explore scholarly data from PKG and compute several measure of knowledge creation. We wanted to propose a python module that allows the use of different existing indicators and those created in the paper within the same framework. 

- This module uses mongoDB, make sure you have installed it before starting and have integrated the data. Neo4J will also be used, check that it is installed.

- The repository is structured as follow:

```bash
├── package
│   ├── cleaner
│   ├── download
│   ├── graphs
│   │   ├── community
│   │   ├── indicators
│   │   └── test
│   ├── stats
│   └── text_algorithm
└── Paper
    ├── Data
    │   ├── Scimago_j_list
    │   └── Wos_j_list
    ├── Notebooks
    └── Results
        └── models
```

- All function used in the paper are store in the package folder. In order to run the analysis made in the paper, please follow the notebooks in the Notebooks folder. They are numbered in order of execution.

- If  you want to use the package for your own projects, follow the small tutorial below:

