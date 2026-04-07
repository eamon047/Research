# Multiplicity 项目说明

这份文件是之后 Codex 处理本项目时的主入口。
如果开启新对话，优先先读这份文件；只有在确实需要查看训练命令、
GPU 设置、LibKGE 运行细节时，再去读 `LibKGE/README_Eamon.md`。

## 项目目标

当前项目的主要目标是复现 EMNLP 2024 论文：

- `Multiplicity/Zhu 等 - 2024 - Predictive Multiplicity of Knowledge Graph Embeddings in Link Prediction.pdf`

重点是复现 `Multiplicity` 论文实验，不是单独研究 LibKGE。

## 代码职责划分

- `Multiplicity/`
  负责 predictive multiplicity 的下游评估代码。
  这里不负责训练 KGE 模型。
- `LibKGE/`
  负责训练、验证、评估 KGE 模型。
  重复训练、多 seed 运行、超参数搜索都在这里完成。

## 当前复现思路

当前默认假设：

- `Multiplicity/configs/`

里的 YAML 文件已经是超参数搜索之后选出来的最终配置。

因此当前流程是：

1. 在 `LibKGE` 中，用同一个配置、不同 seed 反复训练。
2. 为同一个 model-dataset 收集多次独立训练结果。
3. 之后再把这些训练结果交给 `Multiplicity/` 下的脚本做 multiplicity 评估。

## 当前目标

目前优先复现的组合是：

- `RotatE + FB15k-237`

当前在用的配置文件是：

- `LibKGE/examples/RotatE_FB15k237.yaml`

它来自：

- `Multiplicity/configs/RotatE_FB15k237.yaml`

## 数据状态

当前已准备好的数据集是：

- `LibKGE/data/fb15k-237`

该数据集已经下载并完成预处理。

## 当前训练约定

### Seed

我们现在把 seed 直接写在 YAML 文件里，使用：

```yaml
random_seed:
  default: 1
```

之后如果要做 repeated runs，就把这个值改成 `0`、`1`、`2`、`3` 等。

### GPU

当 GPU 编号不稳定时，不要只依赖 YAML 里的 `job.device`。

推荐写法：

```bash
CUDA_VISIBLE_DEVICES=<物理GPU编号> kge start ... --job.device cuda:0
```

含义是：

- 进程只能看到你指定的那张物理 GPU
- 在 LibKGE / PyTorch 内部，这张卡会被当作 `cuda:0`

### 输出目录

当前约定使用：

- `LibKGE/local/multiplicity/RotatE_FB15k237/seed_<n>`

目前已经存在的目录有：

- `LibKGE/local/multiplicity/RotatE_FB15k237/seed_0`
- `LibKGE/local/multiplicity/RotatE_FB15k237/seed_1`

理想结构类似：

```text
LibKGE/local/multiplicity/RotatE_FB15k237/
  seed_0/
  seed_1/
  seed_2/
```

## 论文设定里需要记住的事实

- 论文里的 epsilon-level set 是按 `Hits@K` 定义的。
- 主链路预测表使用的是 `Hits@10`。
- `epsilon = 0.01` 表示绝对容差 `0.01`，也就是 1 个百分点，不是 0.01%。

## 当前 released code 的现实限制

`Multiplicity` 代码不是完全开箱即用的。

已知问题：

- `Multiplicity/main.py` 里仍有占位路径，不能直接无改动运行。
- query answering 相关脚本依赖缓存好的 score tensor，但仓库里没有把那条生成链路讲清楚。
- 因此当前最现实的第一阶段目标，是先把 LibKGE 的 repeated runs 训练好。

## 后续新对话的最简上下文

如果以后新开一个对话，最短可以直接这样说：

```text
请先读 Multiplicity/README_Eamon.md。
只有在需要训练或 GPU 细节时，再读 LibKGE/README_Eamon.md。
我们当前在复现 Multiplicity，第一目标是 RotatE + FB15k-237。
```
