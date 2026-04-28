# Multiplicity_rewrite 说明

这份文件用于说明 `Multiplicity_rewrite/` 的工程角色、本地运行约定，以及它与
`Multiplicity/` 和 `Research/` 文档的分工。

如果开启新对话，和本目录有关的任务应先读这份文件；如果任务已经进入论文结论、
章节组织或具体实验解释，再转去读 `Research/` 下对应文档。

## 1. 这份 README 负责什么

这份文件主要负责：

- 说明 `Multiplicity_rewrite/` 相对于原始 `Multiplicity/` 的定位
- 记录本地环境下可直接运行的分析脚本入口
- 记录当前仍然有效的运行约定与方法口径
- 帮助后续继续做代码维护、结果整理和计算量缩减支线

这份文件**不再**承担下面这些职责：

- 记录每条 thesis 实验线的详细结果
- 维护每个 pattern 的论文解释
- 代替 `Research/` 中的实验记录和写作结构说明

这些内容已经迁移到：

- `Research/thesis_theory.md`
- `Research/thesis_*_experiment.md`
- `Research/thesis_writing.md`
- `Research/thesis_todo.md`

## 2. 项目分工

### `Multiplicity/`

原始 release 目录，保留论文作者的主代码与研究脚本逻辑。

特点：

- 更接近论文 release
- 不直接适合作为当前本地环境下的首选入口
- 适合作为“原始参考实现”阅读和比对

### `Multiplicity_rewrite/`

当前本地维护与 thesis 分析的工作目录。

原则：

- 尽量保留原始 multiplicity 计算逻辑
- 只把本地路径、可运行入口、分析脚本与必要适配迁到这里
- relation-level thesis 分析脚本也统一放在这里

### `LibKGE/`

负责训练、验证和 checkpoint 管理。

它不负责 thesis 分析逻辑，但它提供：

- repeated runs
- config
- checkpoint
- dataset access

## 3. 当前推荐的文档读取顺序

如果任务与 `Multiplicity_rewrite/` 相关，建议顺序如下：

1. 先读本文件
2. 再看相关脚本本身
3. 如果涉及论文定义与结论，再看 `Research/` 对应文档

推荐对应关系：

- 工程入口与运行约定：
  - 本文件
- 定义口径：
  - `Research/thesis_theory.md`
- 单条实验线结果：
  - `Research/thesis_mapping_type_experiment.md`
  - `Research/thesis_inverse_experiment.md`
  - `Research/thesis_symmetry_experiment.md`
  - `Research/thesis_relation_frequency_experiment.md`
- 写作结构与章节衔接：
  - `Research/thesis_writing.md`

## 4. 当前 thesis 主线已经完成到什么程度

截至目前，主线实验块已经基本完成，结构上固定为：

- `mapping type`：主结果
- `inverse`：探索性副结果
- `symmetry`：弱 / 负结果
- `relation frequency`：control variable

因此，`Multiplicity_rewrite/` 之后的主要任务不再是不断扩新的 relation pattern，
而是：

- 维护已有脚本和结果
- 整理图表和表格
- 支持论文写作与结果复查
- 继续计算量缩减支线

## 5. 当前最重要的方法口径

这些口径仍然有效，后续不应在代码维护时随意改变。

### 5.1 主实验对象

当前 thesis 主线的核心数据范围是：

- dataset: `FB15k-237`
- models: `RotatE`, `TransE`
- repeated runs of the same model family
- relation-level analysis

### 5.2 `without` 的含义

主线分析默认使用：

- `baseline = without`

这里的作用是分析 repeated runs 之间的原始 multiplicity，
而不是先引入 voting 缓解。

### 5.3 当前 rewrite 主实验不是论文的严格 epsilon-level set 实现

这点仍然必须牢记。

当前 `Multiplicity_rewrite/main.py` 保留了 multiplicity 主计算逻辑，但它不等于
论文中的严格流程：

- 没有完整实现 “best baseline + epsilon-filtered competing set”
- 当前更接近 “从已有 repeated runs 中抽样后进行 multiplicity 评估”

因此，当前输出应表述为：

- local repeated-run multiplicity results under the current sampling protocol

而不是：

- a strict full reproduction of the original epsilon-level set pipeline

### 5.4 `epsilon` 与指标口径

已核实：

- 论文中的 epsilon-level set 与 `Hits@K` 相关
- 当前 link prediction 主链路主要使用 `Hits@10`
- `epsilon = 0.01` 指绝对差值 `0.01`

但要与当前 rewrite 的采样实现区分开来，不要直接把二者混为一谈。

## 6. 当前本地环境与数据约定

### 环境

当前相关脚本默认使用：

- `LibKGE` conda 环境

如果需要确认环境是否正确，可检查：

```bash
conda activate LibKGE
python -c "import kge; print(kge.__file__)"
```

输出应指向本地仓库内的 `LibKGE/kge/__init__.py`。

### 数据集

当前主线数据集：

- `LibKGE/data/fb15k-237`

### Repeated runs

当前已确认的 run 池包括：

- `LibKGE/local/RotatE_FB15k237/seed_0~7`
- `LibKGE/local/TransE_FB15k237/seed_0~7`

其中如果要做正式的 `TransE` thesis 侧分析，优先使用：

- `TransE_FB15k237`

因为它对应当前统一使用的 `Hits@10` 验证口径。

## 7. 当前保留的主入口脚本

### 7.1 Multiplicity 主实验入口

- `Multiplicity_rewrite/main.py`

用途：

- link-prediction multiplicity 主评估
- 读取 repeated runs
- 生成基础 multiplicity CSV

它不是 thesis 每个小节分析的唯一入口，而是基础结果生成入口。

### 7.2 Mapping Type

- `relation_mapping_analysis.py`
- `support_distribution_analysis.py`
- `mapping_type_analysis.py`
- `mapping_type_side_analysis.py`
- `mapping_type_plot.py`
- `mapping_type_side_plot.py`

### 7.3 Inverse

- `inverse_relation_stats.py`
- `inverse_analysis.py`
- `inverse_mapping_interaction_analysis.py`
- `inverse_relation_stats_v2.py`
- `inverse_analysis_v2.py`
- `inverse_mapping_interaction_analysis_v2.py`
- `inverse_v2_utils.py`

说明：

- `v1` 保留为 baseline / audit trail
- thesis 正式写法以更严格的 `v2` 指标族为主

### 7.4 Symmetry

- `symmetry_relation_stats.py`
- `symmetry_analysis.py`
- `symmetry_analysis_v2.py`
- `symmetry_utils.py`

说明：

- 正式主分析使用 excluding-self 的 symmetry 版本
- raw symmetry 主要用于诊断 self-loop 问题

### 7.5 Relation Frequency

- `relation_frequency_stats.py`
- `relation_frequency_analysis.py`
- `relation_frequency_mapping_interaction.py`
- `relation_frequency_utils.py`

说明：

- 这条线是 control-variable analysis
- 不是第四个 pattern

## 8. 结果目录的一般约定

当前 thesis 相关输出主要放在：

- `results/RotatE_FB15k237/`
- `results/TransE_FB15k237/`

常见子目录包括：

- `link_prediction/`
- `mapping_type/`
- `inverse/`
- `inverse_v2/`
- `symmetry/`
- `symmetry_v2/`
- `relation_frequency/`

一般原则：

- 基础 multiplicity 输出与 thesis-specific analysis 分开放
- 不覆盖旧版分析结果
- 新指标族尽量使用新的子目录，例如 `inverse_v2/`

## 9. Thesis 主线复现入口清单

这一节只记录工程复现链路，不记录实验结论。具体结论仍以 `Research/`
下的实验记录为准。

通用前提：

- 环境：`LibKGE` conda environment
- repeated runs:
  - `LibKGE/local/RotatE_FB15k237/seed_0~7`
  - `LibKGE/local/TransE_FB15k237/seed_0~7`
- 主要参数：`num = 7`、`agg_num = 7`、`k = 10`
- 正式 thesis 口径：`baseline = without`

### 9.1 Mapping Type

输入：

- repeated-run checkpoints under `LibKGE/local/<experiment_name>/`

主要脚本链：

1. `relation_mapping_analysis.py`
   - 导出 by-side relation-level multiplicity table
2. `relation_multiplicity_combined_export.py`
   - 导出 combined relation-level multiplicity table
3. `mapping_type_side_analysis.py`
   - 汇总 by-side grouped statistics
4. `mapping_type_analysis.py`
   - 汇总 combined grouped statistics

主要输出：

- `results/RotatE_FB15k237/mapping_type/by_side/`
- `results/RotatE_FB15k237/mapping_type/combined/`
- `results/TransE_FB15k237/mapping_type/by_side/`
- `results/TransE_FB15k237/mapping_type/combined/`

### 9.2 Inverse

输入：

- training triples from the corresponding LibKGE dataset
- combined relation-level multiplicity table from mapping-type export

主要脚本链：

1. `inverse_relation_stats.py`
   - v1 directional reverse-overlap baseline
2. `inverse_analysis.py`
   - v1 merge and summary
3. `inverse_mapping_interaction_analysis.py`
   - v1 mapping-type interaction
4. `inverse_relation_stats_v2.py`
   - stricter v2 metric family
5. `inverse_analysis_v2.py`
   - v2 merge and summary
6. `inverse_mapping_interaction_analysis_v2.py`
   - v2 mapping-type interaction

主要输出：

- `results/RotatE_FB15k237/inverse/`
- `results/RotatE_FB15k237/inverse_v2/`
- `results/TransE_FB15k237/inverse/`
- `results/TransE_FB15k237/inverse_v2/`

### 9.3 Symmetry

输入：

- training triples from the corresponding LibKGE dataset
- combined relation-level multiplicity table from mapping-type export

主要脚本链：

1. `symmetry_relation_stats.py`
   - 导出 raw symmetry statistics and self-loop diagnostics
2. `symmetry_analysis.py`
   - raw symmetry merge and summary
3. `symmetry_analysis_v2.py`
   - excluding-self-loop symmetry merge and summary

主要输出：

- `results/RotatE_FB15k237/symmetry/`
- `results/RotatE_FB15k237/symmetry_v2/`
- `results/TransE_FB15k237/symmetry/`
- `results/TransE_FB15k237/symmetry_v2/`

### 9.4 Relation Frequency

输入：

- training triples from the corresponding LibKGE dataset
- combined and by-side relation-level multiplicity tables from mapping-type export

主要脚本链：

1. `relation_frequency_stats.py`
   - 导出 relation-level train frequency statistics
2. `relation_frequency_analysis.py`
   - base combined relation-level frequency analysis
3. `relation_frequency_mapping_interaction.py`
   - by-side mapping type x frequency control analysis

主要输出：

- `results/RotatE_FB15k237/relation_frequency/`
- `results/TransE_FB15k237/relation_frequency/`

### 9.5 Thesis Selected Outputs

精选展示版结果统一索引在：

- `results/README.md`

其中 `results/thesis_selected/` 只保留实际结果文件，不再单独维护第二份 README。

## 10. 关于 `README_Eamon` 与 `Research/` 文档的边界

后续维护时，建议遵守：

### 应该写在这里的内容

- 本目录的职责
- 本地脚本入口
- 本地运行约定
- rewrite 相对原始代码的关键差异
- 未来代码维护仍要记住的方法 caveat

### 不应该继续堆在这里的内容

- 每条实验线的最新结论
- 章节组织与论文写作框架
- case study 列表
- 哪个 pattern 是主结果、哪个是弱结果的详细论证

这些内容应继续维护在 `Research/` 下。

## 11. 后续最可能继续用到这份文件的场景

这份文件后面仍然会在下面几类工作中有用：

- 结果复查时快速确认脚本入口
- 文件夹与代码归类整理
- 图表与表格重导出
- 继续维护 `main.py` 的本地可运行版本
- 继续推进“减少计算量”支线

尤其是最后一条：

- 如果后面继续做参数收缩、committee 缩减或其他计算量控制实验，
  这份文件仍应作为 `Multiplicity_rewrite/` 的工程说明入口

## 12. 当前一句话总结

`Multiplicity_rewrite/` 现在的角色，是 thesis 主线分析与后续工程维护的本地工作目录；
它负责脚本、入口和方法约定，而具体实验结论与写作结构应统一放在 `Research/` 下维护。
