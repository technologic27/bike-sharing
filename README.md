
Bike Sharing Trip Duration Prediction
==============================


# Installation

Requires Python3.+ and Docker to run.

Change directory to the project directory.

```sh
cd path/to/project_directory
```
Set-up virtual environment for the first time.

```sh
$ virtualenv venv
```
Activate virtual environment.

```sh
$ source venv/bin/activate
```
Install requirements.

```sh
pip install -r requirements.txt
```
Spin up the Postgres instance and ingest all raw data. Note: If you are having issues with python paths, in the directory where you are importing the script from, run `export PYTHONPATH=.`

```sh
$ docker-compose -f docker-compose-project.yml -d
$ python scripts/ingest_raw.py
```
Most of the configurations are found in the `config.ini` file. Adjust the file location, features selection etc.

Train and test machine learning models

```sh
$ python models/model_run.py
```

The EDA, and model evaluation visualisations are in the `notebooks/` directory. To activate jupyter notebook, type the following command

```sh
$ jupyter notebook
```

# File Submission Information
Business Use Case
---
I have used data of registered users only to predict the trip duration


Deep-dive Analysis of model and feature importance
---
Results of the model are in the notebooks directory.
`notebooks/eda_model_evaluation.ipynb`

### Improvements

 - Write pytests to ensure reproducibility
 - Documentation
 - Additional logging

### Credits

