# LibKGE 本地说明

这份文件记录当前 `LibKGE` 目录下和复现任务直接相关的本地状态。
它主要服务于 `Multiplicity` 复现，不是为了全面介绍 LibKGE。

## 当前状态

- 仓库路径：`/data/satori_hdd1/EamonZhao/EamonFile/LibKGE`
- 当前使用的 conda 环境：`LibKGE`
- 已使用 `pip install -e .` 进行可编辑安装
- 数据集 `fb15k-237` 已经下载并预处理完成

## 数据状态

已准备好的数据集目录：

- `/data/satori_hdd1/EamonZhao/EamonFile/LibKGE/data/fb15k-237`

关键文件包括：

- `dataset.yaml`
- `train.del`
- `valid.del`
- `test.del`
- `entity_ids.del`
- `relation_ids.del`

这些文件说明：

- 原始 `train.txt` 等文本文件保存的是字符串形式的实体/关系
- LibKGE 训练使用的是索引化后的 `*.del`
- `dataset.yaml` 是 LibKGE 识别数据集格式所需的描述文件

## 与当前任务最相关的配置

当前第一目标是复现：

- `RotatE + FB15k-237`

当前实际在用的配置文件：

- `examples/RotatE_FB15k237.yaml`

这个文件来自：

- `Multiplicity/configs/RotatE_FB15k237.yaml`

并且当前已经加入：

```yaml
random_seed:
  default: 1
```

## 重要结构

后续遇到问题时，优先看这些位置：

- `kge/cli.py`
  `kge start`, `kge resume`, `kge valid`, `kge test` 的入口
- `kge/config-default.yaml`
  所有默认配置的主参考
- `kge/job/`
  训练、评估、搜索任务实现
- `kge/model/rotate.py`
  RotatE 模型实现
- `kge/model/rotate.yaml`
  RotatE 相关配置项

## 当前已知的 RotatE FB15k-237 关键参数

这份配置不是简单的 `model: rotate`，而是：

- `model: reciprocal_relations_model`
- `import: [rotate, reciprocal_relations_model]`
- `train.type: negative_sampling`
- `train.loss: bce`
- `lookup_embedder.dim: 256`
- `negative_sampling.num_samples.s: 25`
- `negative_sampling.num_samples.o: 292`
- `rotate.l_norm: 2.0`
- `train.max_epochs: 400`

## GPU 使用约定

经验上，不要只依赖 YAML 里的 `job.device`，因为 GPU 编号可能和实际可见卡不一致。

更稳妥的做法是：

```bash
CUDA_VISIBLE_DEVICES=<物理GPU编号> kge start ... --job.device cuda:0
```

含义：

- 进程只能看到指定的那张物理 GPU
- 在程序内部，这张卡会变成 `cuda:0`

## 当前输出目录约定

我们当前把 repeated runs 放在：

- `local/multiplicity/RotatE_FB15k237/seed_<n>`

目前已经存在：

- `local/multiplicity/RotatE_FB15k237/seed_0`
- `local/multiplicity/RotatE_FB15k237/seed_1`

如果不指定 `--folder`，LibKGE 会默认把结果放到：

- `local/experiments/`

## 常见问题

### 1. `No CUDA GPUs are available`

含义：

- 当前 shell / 会话没有看到可用的 NVIDIA GPU

### 2. `CUDA-capable device(s) is/are busy or unavailable`

含义：

- CUDA 能看到所选 GPU，但这张卡当前不可用
- 可能是被占用、状态异常或驱动层面问题

### 3. `eval.chunk_size` deprecated warning

旧写法会有警告。推荐改成：

```yaml
eval:
  batch_size: 256

entity_ranking:
  chunk_size: 5000
```

当前 `examples/RotatE_FB15k237.yaml` 已经使用了新的 `entity_ranking.chunk_size` 形式。

## 最小运行提醒

如果当前配置文件里的 seed 已经设置好，例如：

```yaml
random_seed:
  default: 1
```

那么可以这样运行：

```bash
cd /data/satori_hdd1/EamonZhao/EamonFile/LibKGE
CUDA_VISIBLE_DEVICES=0 kge start examples/RotatE_FB15k237.yaml --job.device cuda:0 --folder local/multiplicity/RotatE_FB15k237/seed_1
```

如果之后要跑新的独立实验，就修改 YAML 中的 seed，并把输出目录同步改成对应的 `seed_n`。

## 与 Multiplicity 的关系

`LibKGE` 在这里的作用是：

1. 训练同一配置下的多个独立 run
2. 为后续 `Multiplicity` 评估提供 checkpoint 和 config

真正的 multiplicity 指标计算并不在这里，而在：

- `Multiplicity/`

## 新对话时的建议

如果新开对话，不必每次先通读整个 `LibKGE/`。

更省 token 的方式是：

1. 先读 `Multiplicity/README_Eamon.md`
2. 只有在需要训练命令、GPU、seed、输出目录时，再读这份文件
