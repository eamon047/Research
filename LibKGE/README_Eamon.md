# LibKGE Learning Notes

This file records local environment status, what has already been prepared, and
practical notes for continuing to learn and run this codebase.

## Current Status

- Repo path: `/data/satori_hdd1/EamonZhao/EamonFile/LibKGE`
- Conda env used for this project: `LibKGE`
- Installed in editable mode with `pip install -e .`
- Dataset `fb15k-237` has been downloaded and preprocessed

## Data Status

Prepared dataset folder:

- `/data/satori_hdd1/EamonZhao/EamonFile/LibKGE/data/fb15k-237`

Important generated files:

- `dataset.yaml`
- `train.del`
- `valid.del`
- `test.del`
- `entity_ids.del`
- `relation_ids.del`

Meaning of preprocessing:

- Raw files such as `train.txt` use string IDs for entities and relations
- LibKGE training uses indexed triples such as `train.del`
- `dataset.yaml` describes the dataset in the format LibKGE expects

## Key Code Structure

Useful files to read first:

- `kge/cli.py`
  Entry point for `kge start`, `kge resume`, `kge valid`, `kge test`
- `kge/config-default.yaml`
  Master configuration reference
- `kge/job/`
  Training, evaluation, and search job implementations
- `kge/model/rotate.py`
  RotatE implementation
- `kge/model/rotate.yaml`
  RotatE-specific config options
- `README.md`
  Official project overview and usage

## Local Config Files

Two local experiment configs were prepared:

- `examples/fb15k237-rotate-train.yaml`
  A simplified learning-oriented RotatE config
- `examples/fb15k237-rotate-official.yaml`
  Local copy of the official published config for `fb15k-237 + RotatE`

## Official fb15k-237 RotatE Notes

The official result config is not a plain `model: rotate` setup.

Important details:

- `model: reciprocal_relations_model`
- `import: [rotate, reciprocal_relations_model]`
- `train.type: negative_sampling`
- `train.loss: bce`
- `lookup_embedder.dim: 256`
- `negative_sampling.num_samples.s: 25`
- `negative_sampling.num_samples.o: 292`
- `rotate.l_norm: 2.0`
- `train.max_epochs: 400`

So when reproducing the published result, use:

- `examples/fb15k237-rotate-official.yaml`

## GPU Notes

Important lesson:

- Do not rely only on changing `job.device` inside YAML when GPU indexing is unclear
- More stable approach:
  use `CUDA_VISIBLE_DEVICES=<physical_gpu_id>` and keep the program-side device as `cuda:0`

Recommended pattern:

```bash
CUDA_VISIBLE_DEVICES=1 kge start examples/fb15k237-rotate-official.yaml --job.device cuda:0
```

Meaning:

- Only physical GPU 1 is visible to the process
- Inside PyTorch / LibKGE, that visible GPU becomes `cuda:0`

## Errors Encountered Before

### 1. `No CUDA GPUs are available`

Meaning:

- The current shell/session could not see usable NVIDIA devices

Observed checks:

- `nvidia-smi` initially failed to communicate with driver
- `torch.cuda.is_available()` returned `False`

### 2. `CUDA-capable device(s) is/are busy or unavailable`

Meaning:

- The selected GPU was seen by CUDA, but the device was not usable for training at that time
- Possible reasons include device state, allocation policy, or card availability fluctuation

### 3. Deprecated key warning

Observed warning:

- `eval.chunk_size` is deprecated

Preferred newer form:

```yaml
eval:
  batch_size: 256

entity_ranking:
  chunk_size: 5000
```

The official config already uses the newer `entity_ranking.chunk_size` form.

## Minimal Run Reminder

Shortest basic workflow:

```bash
conda activate LibKGE
cd /data/satori_hdd1/EamonZhao/EamonFile/LibKGE
kge start examples/fb15k237-rotate-official.yaml
```

More stable GPU-specific version:

```bash
conda activate LibKGE
cd /data/satori_hdd1/EamonZhao/EamonFile/LibKGE
CUDA_VISIBLE_DEVICES=1 kge start examples/fb15k237-rotate-official.yaml --job.device cuda:0
```

If no `--folder` is provided, LibKGE automatically creates an experiment folder under:

- `local/experiments/`

## Good Next Topics To Learn

- How checkpoints are named and used
- Difference between `kge start`, `kge resume`, `kge valid`, and `kge test`
- What `reciprocal_relations_model` changes compared with plain RotatE
- How validation metrics choose `checkpoint_best.pt`
- How to inspect logs and traces after a run
- How hyperparameter search works in `manual_search`, `ax_search`, and `grash_search`

