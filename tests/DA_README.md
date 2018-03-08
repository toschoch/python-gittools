Git Tools
===============================
author: Tobias Schoch

Description
-----------

A collection of tools to connect to predefined git remote servers and create remote repos, define them as remotes, install local hooks, etc.


Usage
-----
Project tasks are defined with DoIt (http://pydoit.org/), so use
```bat
doit list
```
for seeing a list of the available tasks.

Project Organization
------------

```
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   ├── numbers        <- numerical data to be automatically included in the generated report
    │   ├── figures        <- Generated graphics and figures to be used in reporting
    │   └── report_template.docx
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    ├── conda_reqs.txt     <- The conda file for reproducing the analysis environment, e.g.
    │                         generated with `conda list --export > conda_reqs.txt`
    │
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   ├──__init__.py <- Makes data a Python module
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   ├──__init__.py <- Makes features a Python module
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├──__init__.py <- Makes models a Python module
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       ├──__init__.py <- Makes visualization a Python module
    │       └── utils.py   <- some helper functions for the creation of the figures
    └── dodo.py            <- project task for execution with doit
```
--------