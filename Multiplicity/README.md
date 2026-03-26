# Predictive Multiplicity for Knowledge Graph Embeddings in Link Prediction

## Introduction

This is the implementation of evaluating predictive multiplicity for knowledge graph embedding (KGE) models. We use LibKGE (https://github.com/DeepGraphLearning/KnowledgeGraphEmbedding) to train the KGE models and search for the hyperparameters for the baseline models.

## Files

- HPO.yaml: the template for the configurations of hyperparameter search.
- configs: contains all configuration files used for training KGE models.
- main.py: the script to reproduce the main table (Table 5 in the paper).
- query_answering_1.py/query_answering_1.py: the script to reproduce results for evaluating predictive multiplicity for query answering setting.
- epsilon_evaluation.py: the script to reproduce the results of investigating predictive multiplicity wrt. the change of epsilon.

## Hyperparameter Search

Once you install LibKGE, run 

`kge resume YOUR_CONFIGURATION --search.num_workers TRIAL_NUMBER`

## Model Training

`kge start YOUR_CONFIGURATION`

Please use the configuration files provided in "config" folder to collect competing models.