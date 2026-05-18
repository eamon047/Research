# Thesis Results Index

这个目录用于保存 thesis 主线实验的结果文件，以及后续论文展示版的精选结果。

当前建议不要把所有结果都强行画成图。更合理的做法是：

- `mapping type`：以图为主，表为辅
- `inverse`：以摘要表为主，图为辅
- `symmetry`：以简短负结果表为主
- `relation frequency`：保留为备用控制变量结果，不作为当前默认正文展示

也就是说，当前结果整理的目标不是“每一条线都配一张图”，而是：

> 让别人可以快速找到最值得看的结果文件，并理解每条线最适合用什么形式展示。

## 0. Thesis 展示版精选结果

为了后续论文写作和结果搬运，当前还额外维护了一套展示版精选结果：

- [thesis_selected/](/data/satori_hdd1/EamonZhao/EamonFile/results/thesis_selected)

这里面的文件不是全量原始输出，而是已经筛过口径、适合论文展示的版本。

目录结构：

- `mapping_type/`
  - `legacy/`: 之前直接挑出来的 SVG 图，不删除，只归档
  - `with_table5_baseline/`: 新版带 Table 5 全局参考线的图
  - `mapping_type_selected_summary.csv`: 课件 / 写作使用的分组摘要
- `inverse/`
  - `inverse_selected_summary.csv`
  - `inverse_selected_summary_table.svg`
  - `inverse_selected_relation_baseline_summary.csv`
  - `inverse_selected_relation_baseline_table.svg`
- `symmetry/`
  - `symmetry_selected_summary.csv`
  - `symmetry_selected_summary_table.svg`
  - `symmetry_global_spearman_table.svg`
  - `symmetry_bucket_comparison_table.svg`
- `relation_frequency/`
  - `relation_frequency_selected_summary.csv`

当前统一采用的展示口径：

- threshold: `test_support >= 10`
- `mapping type`: 使用 `by-side` 结果
- `inverse`: 使用 `v2` 指标族
- `symmetry`: 使用 excluding-self 的 `v2` 主定义
- `relation frequency`: 使用 control-variable 解释口径，但当前只作为
  backup / appendix / defense material

精选文件使用建议：

- `mapping type`：优先看 `with_table5_baseline/` 里的新版图
- `inverse / symmetry`：优先看各自 summary csv / table
- `relation frequency`：仅在需要说明 `mapping type` 不是 frequency
  artifact 时查看 summary csv / mapping interaction 结果

口径提醒：

- `mapping_type` 图中的红色线来自原论文 Table 5；本地参考 PDF 保存在
  `Research/references/predictive_multiplicity_paper.pdf`
- 这条线是 `FB15k-237 + without` 的 dataset-level 全局参考值
- 当前箱线图是 thesis 的 relation-level by-side 分布，因此红线应当理解为外部参考线，而不是完全同层级统计量

当前最值得直接看的精选文件：

- [mapping_type_by_side_RotatE_head_t10_with_table5_baseline.svg](/data/satori_hdd1/EamonZhao/EamonFile/results/thesis_selected/mapping_type/with_table5_baseline/mapping_type_by_side_RotatE_head_t10_with_table5_baseline.svg)
- [mapping_type_by_side_RotatE_tail_t10_with_table5_baseline.svg](/data/satori_hdd1/EamonZhao/EamonFile/results/thesis_selected/mapping_type/with_table5_baseline/mapping_type_by_side_RotatE_tail_t10_with_table5_baseline.svg)
- [mapping_type_by_side_TransE_head_t10_with_table5_baseline.svg](/data/satori_hdd1/EamonZhao/EamonFile/results/thesis_selected/mapping_type/with_table5_baseline/mapping_type_by_side_TransE_head_t10_with_table5_baseline.svg)
- [mapping_type_by_side_TransE_tail_t10_with_table5_baseline.svg](/data/satori_hdd1/EamonZhao/EamonFile/results/thesis_selected/mapping_type/with_table5_baseline/mapping_type_by_side_TransE_tail_t10_with_table5_baseline.svg)
- [mapping_type_selected_summary.csv](/data/satori_hdd1/EamonZhao/EamonFile/results/thesis_selected/mapping_type/mapping_type_selected_summary.csv)
- [inverse_selected_summary.csv](/data/satori_hdd1/EamonZhao/EamonFile/results/thesis_selected/inverse/inverse_selected_summary.csv)
- [inverse_selected_relation_baseline_summary.csv](/data/satori_hdd1/EamonZhao/EamonFile/results/thesis_selected/inverse/inverse_selected_relation_baseline_summary.csv)
- [inverse_selected_relation_baseline_table.svg](/data/satori_hdd1/EamonZhao/EamonFile/results/thesis_selected/inverse/inverse_selected_relation_baseline_table.svg)
- [symmetry_selected_summary.csv](/data/satori_hdd1/EamonZhao/EamonFile/results/thesis_selected/symmetry/symmetry_selected_summary.csv)
- [symmetry_global_spearman_table.svg](/data/satori_hdd1/EamonZhao/EamonFile/results/thesis_selected/symmetry/symmetry_global_spearman_table.svg)
- [symmetry_bucket_comparison_table.svg](/data/satori_hdd1/EamonZhao/EamonFile/results/thesis_selected/symmetry/symmetry_bucket_comparison_table.svg)
- [relation_frequency_selected_summary.csv](/data/satori_hdd1/EamonZhao/EamonFile/results/thesis_selected/relation_frequency/relation_frequency_selected_summary.csv)

当前正文展示建议：

- `mapping type` 正文以 `threshold = 10` 的 by-side 图为主
- `inverse / symmetry` 先以 summary tables 为主
- `relation frequency` 暂不主动进入正文展示
- 原始 `5 / 10` 全量图与完整 csv 保留作备查或附录材料

一致性审计记录：

- 已核对 selected summary CSV 中的核心数值均可追溯到对应原始结果目录下的 source CSV，按四位小数一致。
- 对 `inverse / symmetry / relation_frequency` 的 global Spearman 行，selected summary 中的 `n` 用于快速概括 threshold 后的关系数量；正式写作或答辩时，如需精确到每个 prediction metric 的有效样本数，应以原始 `correlation_stats*.csv` 为准。
- 当前需要注意的唯一细节是：`TransE` 在 `test_support >= 10` 的若干 global Spearman 结果中，`hits_r` 的有效样本数为 `182`，而 `alpha_r / delta_r` 的有效样本数为 `181`。这不影响相关系数数值，但不应在正式文本中笼统写成所有三个指标都使用同一个 `n`。

## 1. 当前最值得展示的结果

### 1.1 Mapping Type

这是 thesis 主线中最稳定、最值得可视化展示的部分。

#### RotatE

- [by_side/boxplots.svg](/data/satori_hdd1/EamonZhao/EamonFile/results/RotatE_FB15k237/mapping_type/by_side/boxplots.svg)
  - 主图，最值得展示
- [by_side/summary.txt](/data/satori_hdd1/EamonZhao/EamonFile/results/RotatE_FB15k237/mapping_type/by_side/summary.txt)
  - 主结论文字版
- [by_side/grouped_stats.csv](/data/satori_hdd1/EamonZhao/EamonFile/results/RotatE_FB15k237/mapping_type/by_side/grouped_stats.csv)
  - 分组统计表

#### TransE

- [by_side/boxplots.svg](/data/satori_hdd1/EamonZhao/EamonFile/results/TransE_FB15k237/mapping_type/by_side/boxplots.svg)
  - 跨模型对照主图
- [by_side/mapping_type_side_summary.txt](/data/satori_hdd1/EamonZhao/EamonFile/results/TransE_FB15k237/mapping_type/by_side/mapping_type_side_summary.txt)
  - 跨模型 replication 文字版
- [by_side/mapping_type_side_grouped_stats.csv](/data/satori_hdd1/EamonZhao/EamonFile/results/TransE_FB15k237/mapping_type/by_side/mapping_type_side_grouped_stats.csv)
  - 分组统计表

#### 当前展示建议

- 正文优先展示 `by_side` 图
- `combined` 结果只作为辅助说明
- 这部分是最适合给别人“快速看懂”的结果
- 如果正文只保留一个 threshold，当前优先保留 `test_support >= 10`

### 1.2 Inverse

这部分目前不适合硬画复杂图，更适合用摘要表说明：

- 全局相关性并不支持简单单调规律
- 但高置信 subgroup 在两种模型下都存在

#### RotatE

- [analysis_summary_v2.txt](/data/satori_hdd1/EamonZhao/EamonFile/results/RotatE_FB15k237/inverse_v2/analysis_summary_v2.txt)
- [correlation_stats_v2.csv](/data/satori_hdd1/EamonZhao/EamonFile/results/RotatE_FB15k237/inverse_v2/correlation_stats_v2.csv)
- [bucket_stats_v2.csv](/data/satori_hdd1/EamonZhao/EamonFile/results/RotatE_FB15k237/inverse_v2/bucket_stats_v2.csv)
- [mapping_interaction/summary_v2.txt](/data/satori_hdd1/EamonZhao/EamonFile/results/RotatE_FB15k237/inverse_v2/mapping_interaction/summary_v2.txt)

#### TransE

- [analysis_summary_v2.txt](/data/satori_hdd1/EamonZhao/EamonFile/results/TransE_FB15k237/inverse_v2/analysis_summary_v2.txt)
- [correlation_stats_v2.csv](/data/satori_hdd1/EamonZhao/EamonFile/results/TransE_FB15k237/inverse_v2/correlation_stats_v2.csv)
- [bucket_stats_v2.csv](/data/satori_hdd1/EamonZhao/EamonFile/results/TransE_FB15k237/inverse_v2/bucket_stats_v2.csv)
- [mapping_interaction/summary_v2.txt](/data/satori_hdd1/EamonZhao/EamonFile/results/TransE_FB15k237/inverse_v2/mapping_interaction/summary_v2.txt)

#### 当前展示建议

- 不建议先补散点图
- 更适合整理成：
  - 一张“全局相关性 + high-confidence subgroup”摘要表
  - 一张 case-oriented 辅助表

### 1.3 Symmetry

这部分是弱 / 负结果，当前最适合做成一张短表，而不是继续补图。

#### RotatE

- [analysis_summary_v2.txt](/data/satori_hdd1/EamonZhao/EamonFile/results/RotatE_FB15k237/symmetry_v2/analysis_summary_v2.txt)
- [correlation_stats_v2.csv](/data/satori_hdd1/EamonZhao/EamonFile/results/RotatE_FB15k237/symmetry_v2/correlation_stats_v2.csv)
- [bucket_stats_v2.csv](/data/satori_hdd1/EamonZhao/EamonFile/results/RotatE_FB15k237/symmetry_v2/bucket_stats_v2.csv)

#### TransE

- [analysis_summary_v2.txt](/data/satori_hdd1/EamonZhao/EamonFile/results/TransE_FB15k237/symmetry_v2/analysis_summary_v2.txt)
- [correlation_stats_v2.csv](/data/satori_hdd1/EamonZhao/EamonFile/results/TransE_FB15k237/symmetry_v2/correlation_stats_v2.csv)
- [bucket_stats_v2.csv](/data/satori_hdd1/EamonZhao/EamonFile/results/TransE_FB15k237/symmetry_v2/bucket_stats_v2.csv)

#### 当前展示建议

- 用一张 cross-model summary table 即可
- 不建议为 symmetry 单独追求展示型图表

### 1.4 Relation Frequency

这部分的价值主要在于 control-variable 结论，而不是单独画出“漂亮趋势图”。

当前写作决策已经调整：

- 不默认把它写成正文中的独立实验小节
- 不为了形式对称而给 `inverse` / `symmetry` 追加 frequency control
- 保留它作为 `mapping type` 主结果的备用控制材料
- 只有当需要回应“mapping type 结果是否只是 relation frequency / support
  artifact”时，再引用这部分结果

#### RotatE

- [analysis_summary.txt](/data/satori_hdd1/EamonZhao/EamonFile/results/RotatE_FB15k237/relation_frequency/analysis_summary.txt)
- [correlation_stats.csv](/data/satori_hdd1/EamonZhao/EamonFile/results/RotatE_FB15k237/relation_frequency/correlation_stats.csv)
- [bucket_stats.csv](/data/satori_hdd1/EamonZhao/EamonFile/results/RotatE_FB15k237/relation_frequency/bucket_stats.csv)
- [mapping_interaction/summary.txt](/data/satori_hdd1/EamonZhao/EamonFile/results/RotatE_FB15k237/relation_frequency/mapping_interaction/summary.txt)

#### TransE

- [analysis_summary.txt](/data/satori_hdd1/EamonZhao/EamonFile/results/TransE_FB15k237/relation_frequency/analysis_summary.txt)
- [correlation_stats.csv](/data/satori_hdd1/EamonZhao/EamonFile/results/TransE_FB15k237/relation_frequency/correlation_stats.csv)
- [bucket_stats.csv](/data/satori_hdd1/EamonZhao/EamonFile/results/TransE_FB15k237/relation_frequency/bucket_stats.csv)
- [mapping_interaction/summary.txt](/data/satori_hdd1/EamonZhao/EamonFile/results/TransE_FB15k237/relation_frequency/mapping_interaction/summary.txt)

#### 当前展示建议

- 不作为默认正文展示
- 如需使用，优先用一张 compact table 或一段文字说明
  `mapping type` effect survives frequency stratification
- 不建议单独补 frequency scatter

## 2. 当前建议的结果展示层级

### 第一层：正文主展示

- `mapping type` by-side boxplots
- `mapping type` 的跨模型对照

### 第二层：正文或附录摘要表

- `inverse` cross-model summary table
- `symmetry` cross-model summary table
- `relation frequency` cross-model summary table only if a control-variable
  objection needs to be addressed

### 第三层：附录 / 备查文件

- 各目录下的完整 `csv`
- 所有 `summary.txt / analysis_summary.txt`
- case-specific 明细表
- `relation frequency` full outputs and selected summary

## 3. 当前最专业的整理策略

从 thesis 展示角度，当前最合理的下一步不是一口气补很多图，而是：

1. 保留 `mapping type` 现有图作为主图
2. 为 `inverse / symmetry` 各做一张简洁摘要表
3. 暂缓 `relation frequency` 的正文展示，保留为控制变量备查
4. 如果之后确实需要，再补极少量额外图

原因是：

- `mapping type` 的图像信号最强
- `inverse / symmetry` 更适合用“简洁结果表 + 一句话结论”表达
- `relation frequency` 对主结果有防守价值，但作为独立正文线条会显得
  不够对称，因为它没有同样控制 `inverse` 和 `symmetry`
- 这样结果会更容易给别人看懂，也更符合当前 thesis 的层级结构

## 4. 当前一句话总结

目前只有 `mapping type` 拥有真正适合作为主展示的图；`inverse` 和
`symmetry` 更适合整理成清楚的 cross-model summary tables；`relation
frequency` 暂时保留为控制变量备查，而不是为了形式统一强行写入正文。
