# Predictive Multiplicity for KGE Link Prediction

This directory contains the downstream evaluation code for the EMNLP 2024 paper
"Predictive Multiplicity of Knowledge Graph Embeddings in Link Prediction".
It is not a full training framework. Model search and training are expected to
be run with `LibKGE/`, and the scripts here consume trained LibKGE experiment
folders and, for query-answering experiments, cached score tensors.

The paper PDF is included here:

- `Zhu 等 - 2024 - Predictive Multiplicity of Knowledge Graph Embeddings in Link Prediction.pdf`

## What Is In This Folder

- `configs/`
  Selected LibKGE config files used to train the base KGE models.
- `HPO.yaml`
  A template for LibKGE hyperparameter search.
- `main.py`
  Reproduces the link-prediction multiplicity table by loading multiple trained
  LibKGE runs and evaluating Hits@k, epsilon, ambiguity, and discrepancy.
- `epsilon_evaluation.py`
  Research script for the epsilon-sensitivity analysis described in the paper.
  It is still specialized to the original setup and has not been fully cleaned up.
- `query_answering_1.py`
  Top-1 query-answering multiplicity evaluation from cached score tensors.
- `query_answering_10.py`
  Top-10 query-answering multiplicity evaluation from cached score tensors.

## Relationship To `LibKGE`

The intended workflow is:

1. Use `LibKGE` to preprocess datasets, run hyperparameter search, and train
   multiple runs with different random seeds.
2. Store those trained runs in a directory layout like:

```text
<experiments-root>/
  TransE/
    TransE_FB15k237/
      run_001/
        config.yaml
        checkpoint_best.pt
      run_002/
        ...
  ComplEx/
    ComplEx_WN18RR/
      ...
```

3. Use the scripts in this folder to aggregate those runs and compute
   multiplicity metrics.

For query-answering experiments, an additional cached score directory is needed:

```text
<scores-root>/
  ConvE/
    ConvE_FB15k/
      relation_mask.pkl
      one_mask.pt
      run_001_o.pt
      run_001_s.pt
      ...
```

This repository currently does not include the script that generates those
`*_o.pt` / `*_s.pt` score caches. That is an actual gap in the released code,
so top-1 and top-10 query-answering reproduction still depends on reconstructing
that preprocessing step from the paper or the original author environment.

## Environment

The scripts expect:

- `LibKGE` installed in editable mode
- a Python environment with `torch`, `pandas`, `yaml`, `tqdm`, `scipy`
- processed datasets under `LibKGE/data/`

Example setup:

```bash
cd /data/satori_hdd1/EamonZhao/EamonFile/LibKGE
pip install -e .
```

## Reproducing Training With `LibKGE`

### 1. Hyperparameter search

Use `HPO.yaml` as a template, or start from one of the configs in `configs/`.

```bash
cd /data/satori_hdd1/EamonZhao/EamonFile/LibKGE
kge resume /path/to/search-config.yaml --search.num_workers 4
```

### 2. Train the selected configuration

```bash
cd /data/satori_hdd1/EamonZhao/EamonFile/LibKGE
kge start /data/satori_hdd1/EamonZhao/EamonFile/Multiplicity/configs/RotatE_FB15k237.yaml
```

To study multiplicity, you need multiple independently trained runs for the
same model-dataset pair, typically by changing the random seed or rerunning the
same configuration into different output folders.

## Reproducing Table-Style Link Prediction Results

`main.py` now takes an explicit experiment root instead of the placeholder path
that was in the original release.

Example:

```bash
cd /data/satori_hdd1/EamonZhao/EamonFile
python Multiplicity/main.py \
  --experiments-root /path/to/finished \
  --models TransE RESCAL DistMult ComplEx ConvE \
  --datasets WN18 WN18RR FB15k FB15k237 \
  --num 10 \
  --agg-num 8 \
  --k 10 \
  --seed 0 \
  --output results/results_num10_agg8_k10.csv
```

Expected input layout:

- `--experiments-root/<Model>/<Model>_<Dataset>/<run>/config.yaml`

The script loads each run as a LibKGE evaluation job and then compares:

- `without`
- `major`
- `borda`
- `range`

The output CSV contains:

- `Hits`
- `Epsilon`
- `Alpha`
- `Delta`

## Reproducing Query-Answering Results

Both scripts now take explicit paths for experiments, cached scores, and data.

### Top-1 query answering

```bash
python Multiplicity/query_answering_1.py \
  --experiments-root /path/to/finished \
  --scores-root /path/to/filtered_scores \
  --data-root /data/satori_hdd1/EamonZhao/EamonFile/LibKGE/data \
  --models TransE RotatE ComplEx RESCAL DistMult ConvE \
  --datasets WN18 WN18RR FB15k237 FB15k \
  --num 2 \
  --agg 2 \
  --seed 0
```

### Top-10 query answering

```bash
python Multiplicity/query_answering_10.py \
  --experiments-root /path/to/finished \
  --scores-root /path/to/multi_scores \
  --data-root /data/satori_hdd1/EamonZhao/EamonFile/LibKGE/data \
  --models ConvE \
  --datasets FB15k \
  --num 2 \
  --agg 2 \
  --seed 0
```

Outputs are written under `local/` by default as:

- `*.log`
- `*.pkl`

## Notes On The Released Code

The original release had several issues that make reproduction harder than it
should be:

- `main.py` used a placeholder experiment path (`.../`).
- query-answering scripts hardcoded the authors' absolute filesystem paths.
- `query_asnwering_10.py` had a filename typo.
- the score-cache generation step for query answering is not included here.
- some scripts are still research code rather than polished command-line tools.

This README and the script entry points were updated locally to remove the
machine-specific assumptions and make the existing pieces runnable in a normal
workspace layout.
