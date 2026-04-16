# Multiplicity 项目说明

这份文件是之后 Codex 处理本项目时的主入口。
如果开启新对话，优先先读这份文件；只有在确实需要查看训练命令、
GPU 设置、LibKGE 运行细节时，再去读 `LibKGE/README_Eamon.md`。

## 项目目标

当前项目的主要目标是复现 EMNLP 2024 论文：

- `Multiplicity/paper.pdf`

重点是复现 `Multiplicity` 论文实验，不是单独研究 LibKGE。

当前已经进一步明确：

- 短期最优先目标不是严格复现全文，而是先把 `link prediction` 主实验链路稳定跑通。
- 之后再基于稳定输出去推进 relation pattern 与 multiplicity 的论文分析。

## 协作规范

之后如果 Codex 需要修改现有文件，默认遵循下面的规则：

- 优先在原文件基础上增量补充，不要随意覆盖或删除已有内容。
- 如果一个文件里已有用户自己整理的命令、备注、历史记录，除非用户明确要求清理或替换，否则应保留。
- 如果需要重写某个文件，先明确说明原因；若只是补充新内容，应尽量追加或局部修改。

之后如果 Codex 参与方案讨论，默认采用下面的角色要求：

- 以 KG / LLM 方向的专业研究导师视角分析问题，而不是仅仅做执行助手。
- 保持独立判断和批判性思维，不要为了迎合用户而默认认可一个方案。
- 如果用户的实验设计、指标口径、复现路径或结论表达不够严谨，要直接指出问题在哪里。
- 在给建议时，优先区分“严格复现论文”与“工程上可行的近似验证”这两种口径。
- 对论文、代码、实验日志的关键结论，尽量基于文本或实现核实，不要凭印象回答。

## 代码职责划分

- `Multiplicity/`
  负责 predictive multiplicity 的下游评估代码。
  这里不负责训练 KGE 模型。
- `LibKGE/`
  负责训练、验证、评估 KGE 模型。
  重复训练、多 seed 运行、超参数搜索都在这里完成。

## 当前建议的代码入口

当前要特别区分：

- `Multiplicity/main.py`
- `Multiplicity_rewrite/main.py`

两者定位不同：

- `Multiplicity/main.py`
  更接近论文 release 的原始研究脚本。
  它保留了原作者的主计算逻辑，但底部实验入口仍是占位路径和批处理写法，
  不适合作为当前本地环境的首选可运行入口。
- `Multiplicity_rewrite/main.py`
  当前本地 debug 与运行的首选入口。
  原则是：尽量保留 `main.py` 的主体计算逻辑，只把本地路径、单实验入口、
  以及必要的显存适配改写到 `Multiplicity_rewrite/` 下。

因此，如果新开对话，关于“当前能跑的 multiplicity 主实验”应优先看：

- `Multiplicity_rewrite/main.py`

而不是直接把：

- `Multiplicity/main.py`

当作现成可运行脚本。

## 当前复现思路

当前默认假设：

- `Multiplicity/configs/`

里的 YAML 文件已经是超参数搜索之后选出来的最终配置。

因此当前流程是：

1. 在 `LibKGE` 中，用同一个配置、不同 seed 反复训练。
2. 为同一个 model-dataset 收集多次独立训练结果。
3. 之后再把这些训练结果交给 `Multiplicity/` 下的脚本做 multiplicity 评估。

当前已额外明确一条本地 debug 原则：

- 先把主实验代码跑通，再继续细化论文问题和 relation-level 分析

也就是说，当前阶段最重要的是：

- “评估链路是否稳定可运行”

而不是：

- “是否已经严格实现论文里的 baseline 选择与 `epsilon` 构造流程”

## 当前目标

目前优先复现的组合是：

- `RotatE + FB15k-237`
- `TransE + FB15k-237`

其中当前更适合作为代码调试和评估链路修正入口的是：

- `RotatE + FB15k-237`

而 `TransE + FB15k-237` 当前的定位更偏向：

- 按更贴近论文口径的验证标准，重新生成一套更干净的 repeated runs

当前阶段还有一个进一步收缩后的目标：

- 先跑通 `RotatE + FB15k-237` 的 multiplicity 主实验
- 在此基础上再平移到 `TransE`，以及后续的 relation-pattern 分析

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

- `RotatE_FB15k237` 目前已有 `seed_0` 到 `seed_7` 共 8 个 run。
- `TransE_FB15k237` 目前也已有 `seed_0` 到 `seed_7` 共 8 个 run。
- 这些目录里的 `config.yaml` 都记录了对应的 `random_seed.default`。
- 目前没有发现“目录名不同，但实际用了同一个 seed”的问题。

进一步核查 `trace.yaml` 后可确认：

- 每个 run 都只有 1 个独立的 `train job_id` 和 1 个 `eval job_id`。
- 没有看到 `job_resumed` 事件。
- 前几个 epoch 的 loss 轨迹彼此不同。

因此当前可以把：

- `RotatE_FB15k237/seed_0~7`
- `TransE_FB15k237/seed_0~7`

都视为独立训练结果集合。

另外，目前还存在一套额外目录：

- `TransE_FB15k237_N/seed_0~7`

这里的 `_N` 含义是：

- new

并且其关键差异是：

- 该套 run 的验证指标口径更贴近 `Hits@10`

因此：

- 如果后续需要更贴近论文口径地使用 `TransE`
- 当前优先考虑 `TransE_FB15k237_N`

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

但要特别记住：

- 论文中的 `epsilon` 更多是用来构造 competing model set 的准入条件
- 当前 released `Multiplicity/main.py` 并没有严格实现这一构造过程

当前代码实际做的是：

- 从已有 runs 中随机抽样
- 然后对抽到的模型组事后统计 `epsilon = max(hits) - min(hits)`

因此当前一定要区分：

- 论文中的严格 `epsilon`-level set 构造
- 当前本地代码里的随机抽样 multiplicity 评估

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

## 当前 RotatE / TransE 数据池的结论

目前两套结果都已检查到 `seed_0~7`：

- `RotatE_FB15k237`
- `TransE_FB15k237`

如果按论文口径，用每个 run 在训练过程中达到过的最佳验证 `Hits@10`
来比较：

- `RotatE` 当前最佳 run 是 `seed_3`
- `TransE` 当前最佳 run 是 `seed_1`

并且：

- 两套结果中，其余 run 与各自最佳 run 的 `Hits@10` 差距都小于 `0.01`

因此从“是否足够接近，可以构成 epsilon-level set 的近似样本”这个角度看：

- `RotatE` 当前可用
- `TransE` 当前也可用

这意味着：

- 对每一套结果，都可以从 8 个 run 里选 1 个 baseline，再选出至少 6 个近似模型，外加 1 个备用 run。

但在当前 debug 阶段，实际运行脚本时采用的是更务实的近似设定：

- 从 8 个 run 中取 7 个进入主实验
- 当前参数设定为：`num = 7`, `agg_num = 7`, `k = 10`

这里应理解为：

- 在 7 个近似等价 run 上进行 multiplicity 评估

而不是：

- 已经严格完成“best baseline + 6 个由 `epsilon` 过滤出的 competing models”的论文口径实现

## 目前最重要的技术风险

当前最大的风险已经不是 seed，也不是 epsilon，而是：

- 后续到底用哪个 checkpoint 来代表每个 run

原因是：

- 论文这里构造 baseline / competing models 的标准，本质上围绕验证 `Hits@10`
- 但 LibKGE 默认的 `checkpoint_best.pt` 是按验证 `MRR` 选出来的

这会导致：

- 某个 run 的“MRR 最优 epoch”
- 和它的“Hits@10 最优 epoch”

不一定相同。

此外，当前目录里通常只保留最后几个 numbered checkpoints，
因此部分 run 的“Hits@10 最优 epoch 对应 checkpoint”已经不在本地目录里。

所以目前要明确区分两种口径：

- 工程上先跑通：直接使用现有 `checkpoint_best.pt`
- 更严格地贴近论文：应尽量使用“验证 `Hits@10` 最优 epoch”的 checkpoint

当前更合理的优先级是：

- 先利用现有 repeated runs 把 `Multiplicity` 代码改到可运行
- 再决定是否为了更严格的论文口径补跑部分 checkpoint

## 关于 `kge` 包

`Multiplicity` 里的：

```python
import kge
```

这里的 `kge` 并不是另外一个神秘外部项目，而是：

- `LibKGE` 仓库通过 `pip install -e .` 安装出来的本地 Python 包

目前已确认：

- `LibKGE` conda 环境中可以成功 `import kge`
- 对应路径为 `LibKGE/kge/__init__.py`

因此当前 multiplicity 主实验应默认使用：

- `LibKGE` conda 环境

如果之后新开对话，需要先确认：

```bash
conda activate LibKGE
python -c "import kge; print(kge.__file__)"
```

只要输出的是：

- `.../EamonFile/LibKGE/kge/__init__.py`

就说明当前环境口径是对的。

## 当前本地可运行入口的已知修改

当前 `Multiplicity_rewrite/main.py` 的本地版本，已经采用了下面这些最小修改：

1. 不再批量遍历所有论文模型和数据集。
2. 当前只固定跑一个实验组合。
3. 当前默认实验目录为：
   - `LibKGE/local/multiplicity/RotatE_FB15k237`
4. 当前默认参数为：
   - `num = 7`
   - `agg_num = 7`
   - `k = 10`
5. 为了避免显存不足，当前额外做了两处本地适配：
   - 将 `eval.batch_size` 强制设为 `16`
   - 在打分时使用 `torch.no_grad()`

这里要明确：

- 这两处调整只影响显存占用与运行时间
- 不改变 multiplicity 评估的定义

## 当前 rewrite 版到底在算什么

这一点非常重要，因为当前 `Multiplicity_rewrite/main.py` 的可运行版本，
虽然保留了原始 `main.py` 的主计算逻辑，但它并不等于论文里的严格实验流程。

### 1. 它没有实现“先选 best baseline，再按 epsilon 构造 competing set”

当前代码不会自动执行下面这条严格论文流程：

1. 先选出 performance 最好的 baseline model
2. 再按 `epsilon` 过滤出 competing models
3. 最后只在这个 `epsilon`-level set 上评估 multiplicity

当前代码实际做的是：

- 先读取一个已有 run 池
- 再从 run 池中随机抽样
- 然后直接在这些抽样结果上计算 `Hits / Epsilon / Alpha / Delta`

因此当前应当明确区分：

- 论文原意：best baseline + epsilon-filtered competing set
- 当前 released-code / rewrite 口径：randomly sampled run groups

### 2. `NUM` 和 `AGG_NUM` 的真实含义

当前代码中：

- `NUM`
  表示要生成多少个待比较输出
- `AGG_NUM`
  表示每个输出对应的 committee 大小

它们都不是：

- “总模型数”
- “baseline 数量”

例如当前实际目录里有 `8` 个 run，而参数设为：

- `NUM = 7`
- `AGG_NUM = 7`

这表示的是：

- 从 `8` 个 run 中随机选出 `7` 个 baseline index
- 对每个 baseline index，再构造一个大小为 `7` 的 committee
- 最终得到 `7` 个 outputs 用于比较

### 3. `without` 不是“和最优模型比较”

当前代码在 `without` 情况下，并不是“拿一个最优模型去和 aggregated model 比”。

它实际做的是：

- 对每个 sampled group，只取该 group 最后一个模型的输出
- 这个“最后一个模型”其实就是构造 group 时 append 进去的那个 baseline index

因此：

- `without` 模式下，比较的是多个单模型输出之间的 multiplicity
- 不是“一个固定最优模型 vs 若干 competing models”

### 4. `major / borda / range` 也不是论文里的两层 voting

论文原意更接近：

- 对 `S'ε(M*)` 里的每一个模型
- 再额外训练一组模型做 aggregation
- 最后比较这些 aggregated models

这意味着论文里的 voting 是更严格的两层过程。

但当前代码并没有额外训练第二层模型。

当前 `major / borda / range` 做的是：

- 直接对现有 run 池里的 committee 做投票聚合

因此当前 voting 结果应理解为：

- 现有 run 池上的直接 committee voting

而不是：

- 论文里严格 two-level voting protocol 的完整复现

### 5. Alpha / Delta 到底是对谁算的

当前代码会先生成一组 outputs，然后：

- `Alpha` 在这组 outputs 之间计算
- `Delta` 也是在这组 outputs 之间计算

需要特别注意：

- 当前代码里的 `Delta` 基准不是“best model”
- 而是 `ranks[0]`，也就是当前输出列表中的第一个结果

因此：

- 当前 `Delta` 的基准是“当前 sampled outputs 中的第一个输出”
- 不是论文语义下经过选择的最优 baseline

### 6. 当前结果应该怎么表述

因此当前 `Multiplicity_rewrite/main.py` 跑出来的结果，应当表述为：

- 在当前 run 池和当前 sampling / committee 设定下的 multiplicity 结果

而不应直接表述为：

- 严格复现论文中“best baseline + epsilon-level set + two-level voting”的最终结果

更准确地说，当前结果是：

- released-code 口径下
- 本地可运行版本
- 单模型单数据集
- 小规模 committee 设置

的 multiplicity 结果

## 当前已验证的一次成功运行

当前已经在本地服务器环境中成功跑通一次：

- 入口：`Multiplicity_rewrite/main.py`
- 组合：`RotatE + FB15k-237`
- 参数：`num = 7`, `agg_num = 7`, `k = 10`
- 结果文件：`results/RotatE_FB15k237_num7_agg7_k10.csv`

该次运行的 wall-clock 总耗时约为：

- `16:44.44`

因此后续可以把：

- 约 15 到 20 分钟

视为当前这一组合的一次主实验运行时间量级参考。

## 当前结果与论文 Table 5 的关系

当前已对下面两份结果做过一次直接对照：

- 本地结果：`results/RotatE_FB15k237_num7_agg7_k10.csv`
- 论文结果：`Multiplicity/paper.pdf` 中 `Table 5` 的 `RotatE + FB15k237`

当前判断是：

- `Borda` 与 `range` 的数值非常接近论文
- `without` 的 `Hits` 接近，但 `Alpha / Delta` 偏高
- `major` 偏差最大，尤其 `Hits` 明显低于论文

因此当前更合理的总结是：

- 当前本地结果与论文在趋势上吻合
- 其中 `Borda` 和 `range` 可视为高度接近
- 但整体还不应表述为严格数值复现

这与下列因素有关：

- 当前仍使用小规模 run 池
- 当前 voting 只是对现有 runs 直接聚合
- 当前 `RotatE_FB15k237` 仍是旧的 `MRR` 口径 runs

## 当前已知但暂不优先处理的 warning

以下 warning 目前都已经见过，并且不影响实验定义：

- `torch.load(... weights_only=False)` 的 `FutureWarning`
- `torch.cuda.sparse.FloatTensor(...)` 的 deprecated / warning

当前处理原则是：

- 只要没有 traceback、OOM 或显式 `RuntimeError`
- 且 GPU 与 Python 进程仍在工作
- 就可以先视为程序仍在正常运行

## 当前推荐运行命令

当前推荐的运行方式是：

```bash
cd /data/satori_hdd1/EamonZhao/EamonFile
conda activate LibKGE
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
/usr/bin/time -v python Multiplicity_rewrite/main.py 2>&1 | tee run_mul.log
```

这样做的好处是：

- 使用正确的 `LibKGE` 环境
- 对显存碎片更稳一些
- 运行结束后可直接在日志里查看总耗时

其中最应关注的时间字段是：

- `Elapsed (wall clock) time`

## 关于 query-answering 脚本的当前定位

当前不建议优先投入：

- `Multiplicity/query_answering_1.py`
- `Multiplicity/query_asnwering_10.py`

原因包括：

- 依赖额外 score cache
- 发布代码中仍残留作者机器路径
- 当前主线是 link prediction multiplicity，不是 query-answering 扩展

此外，这两份脚本里还有一个值得记住的可疑点：

- `s_tensor.append(get_top10(o_agg_scores))`

这里看起来很可能本应使用：

- `s_agg_scores`

因此在没有专门核实前，不建议把 query-answering 部分作为当前主线结果来源。

## 关于 LibKGE 验证指标与 checkpoint_best 的关系

这里已经专门核实过一次 LibKGE 的实现逻辑。

结论是：

- `checkpoint_best.pt` 的选择标准会自动跟随 `valid.metric`
- 但 numbered checkpoints 的保留 / 删除策略，不会因为 `valid.metric` 改变而自动改变

也就是说：

- 如果把 `valid.metric` 从默认的 `MRR` 改成 `Hits@10`
- 那么下一轮训练里，`checkpoint_best.pt` 会改为按 `Hits@10` 选
- 这一点对后续 multiplicity 使用“每个 run 的 best checkpoint”是有帮助的

但同时要知道：

- 这并不会自动保留更多中间 epoch 的 checkpoint
- 不过如果当前策略只是“每个 seed 最终只使用一个代表模型”，
  那么现阶段不一定需要额外修改 checkpoint 保留策略

## 当前关于 TransE 重跑的决定

目前已做出的决定是：

- 对 `TransE_FB15k237`，先只修改验证指标口径，不额外修改 checkpoint 保留策略

原因是：

- 当前更关注的是让 `checkpoint_best.pt` 不再按 `MRR` 选
- 而是按更贴近论文定义的 `Hits@10` 口径来选

当前已在以下配置文件中完成修改：

- `LibKGE/examples/TransE_FB15k237.yaml`

修改内容是：

```yaml
valid:
  metric: hits_at_10_filtered_with_test
```

这里选用：

- `hits_at_10_filtered_with_test`

而不是默认的：

- `mean_reciprocal_rank_filtered_with_test`

这样做的含义是：

- 之后新跑出来的 `TransE` repeated runs，其 `checkpoint_best.pt`
  将按 `Hits@10` 相关指标选取

当前这样做被视为一个务实折中：

- 先把 run 内部 best checkpoint 的选择标准改正确
- 暂时不扩大 checkpoint 保留范围
- 后续优先把 `Multiplicity` 代码改到能吃下这些结果

## 关于 RotatE 指标与 LibKGE README 数字的比较

目前要特别注意，不要把以下两类数字直接比较：

- 训练日志里的验证指标
- `LibKGE/README.md` 里的最终结果表

因为 `LibKGE/README.md` 里明确写的是：

- `filtered MRR and HITS@k on test data`

也就是说，README 表里的 `RotatE + FB15k-237 = Hits@10 0.522`
是测试集结果，不是训练过程中的验证集结果。

而我们之前在 `trace.yaml` 里一直看的主要是：

- `split: valid`
- `hits_at_10_filtered`

所以：

- 直接把当前日志里大约 `0.49x` 的验证结果，与 README 里的 `0.522`
  进行一一对照，并不严格。

另一个需要注意的点是：

- `filtered` 不是导致数值偏低的原因

`filtered` 的含义是：

- 在 ranking 评估时，把其他已知为真的三元组过滤掉，避免把正确答案误算成负例

一般来说：

- `filtered` 指标应当不低于原始 `unfiltered` 指标

因此当前数值差距的主要来源不是 “用了 filtered”，而是：

- 你在看验证集而不是测试集
- 你在看 `hits_at_10_filtered`，而不是最终测试设置下的报告值
- 以及当前 run 的 checkpoint 选择标准仍默认跟随 `MRR`

## 下一步最合理的实验口径

如果下一步继续推进 `RotatE + FB15k-237`，当前最合理的表述是：

- 先基于现有 8 个独立 run，做一个缩小版的 multiplicity 评估。
- baseline 可以先从这些 run 里按验证 `Hits@10` 最高者选出。
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
LibKGE/local/multiplicity/RotatE_FB15k237 里已有 seed_0 到 seed_7 八个独立 run。
epsilon 已确认是按 Hits@10 的绝对差值 0.01 来判定，不是按 MRR。
```
