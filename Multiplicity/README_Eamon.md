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
- `LibKGE/local/multiplicity/RotatE_FB15k237/seed_2`
- `LibKGE/local/multiplicity/RotatE_FB15k237/seed_3`
- `LibKGE/local/multiplicity/RotatE_FB15k237/seed_4`
- `LibKGE/local/multiplicity/RotatE_FB15k237/seed_5`

理想结构类似：

```text
LibKGE/local/multiplicity/RotatE_FB15k237/
  seed_0/
  seed_1/
  seed_2/
```

## 当前已核实的 repeated runs 状态

已确认：

- `seed_0` 到 `seed_5` 这 6 个目录都存在。
- 每个目录里的 `config.yaml` 都记录了对应的 `random_seed.default`。
- 目前这 6 个 run 没有发现“忘记改 seed，结果重复用了同一个 seed”的问题。

对应关系是：

- `seed_0 -> random_seed.default = 0`
- `seed_1 -> random_seed.default = 1`
- `seed_2 -> random_seed.default = 2`
- `seed_3 -> random_seed.default = 3`
- `seed_4 -> random_seed.default = 4`
- `seed_5 -> random_seed.default = 5`

此外，`trace.yaml` 也支持这个结论：

- 6 个目录的训练 `job_id` 都不同。
- 没有看到 `job_resumed` 事件。
- 前几个 epoch 的 loss 轨迹彼此不同。

因此当前可以把这 6 个 run 视为 6 次独立训练结果。

## 论文设定里需要记住的事实

- 论文里的 epsilon-level set 是按 `Hits@K` 定义的。
- 主链路预测表使用的是 `Hits@10`。
- `epsilon = 0.01` 表示绝对容差 `0.01`，也就是 1 个百分点，不是 0.01%。
- 更具体地说，在当前主实验里，是否属于近似模型，要看 `Hits@10` 的绝对差值是否 `<= 0.01`，不是看 `MRR`。

## 关于 epsilon 的核实结果

这件事已经结合论文和代码核实过：

- 论文定义里，baseline 和 competing model 的差距是按 `Hits@K` 定义的，不是按 `MRR`。
- 对当前 link prediction 主实验，代码里使用的是 `k = 10`。
- `Multiplicity/main.py` 中的 `epsilon` 实现是同一组模型的 `max(hits) - min(hits)`。

因此当前语境下：

- `epsilon = 0.01`

等价于：

- `Hits@10` 的绝对差距不超过 `0.01`

也就是：

- 不超过 1 个百分点

## 当前 6 个 run 与 epsilon 条件的关系

当前已经做过一次粗核对：

- 若按“验证集上达到过的最高 `Hits@10`”来选 baseline，
  那么当前 6 个 run 里最强的是 `seed_3`。
- 其余 `seed_0`、`seed_1`、`seed_2`、`seed_4`、`seed_5`
  与最佳 run 的 `Hits@10` 差距都显著小于 `0.01`。

这意味着：

- 这 6 个 run 目前足够支持一个“小规模的 epsilon-level set 近似实验”。

但要注意：

- 这只能算是一个 `6-model` 的 pilot / 缩小版复现。
- 它不能直接等同于论文里“收集到 10 个 competing models”的完整设定。

## 下一步最合理的实验口径

如果下一步继续推进 `RotatE + FB15k-237`，当前最合理的表述是：

- 先基于现有 6 个独立 run，做一个缩小版的 multiplicity 评估。
- baseline 可以先从这 6 个 run 里按验证 `Hits@10` 最高者选出。
- 剩余满足 `epsilon <= 0.01` 的 run 可先作为 competing models。

同时要记住一个重要细节：

- 不要直接默认使用 `checkpoint_best.pt` 作为论文意义下的最佳模型。
- LibKGE 的 `checkpoint_best.pt` 可能是按验证 `MRR` 选出来的。
- 而论文这里构造 epsilon-level set 的基准应当是验证 `Hits@10`。
- 因此后续真正进入 `Multiplicity` 评估前，最好先确定每个 run
  “验证 `Hits@10` 最高的 epoch” 对应的是哪个 checkpoint。

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
LibKGE/local/multiplicity/RotatE_FB15k237 里已有 seed_0 到 seed_5 六个独立 run。
epsilon 已确认是按 Hits@10 的绝对差值 0.01 来判定，不是按 MRR。
```
