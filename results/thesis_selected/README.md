# Thesis Selected Outputs

这个目录只保留 thesis / zemi 最常用的展示版结果，并按主题分组。

## 结构

- `mapping_type/`
  - `legacy/`: 之前直接挑出来的 SVG 图，不删除，只归档
  - `with_table5_baseline/`: 新版带 Table 5 全局参考线的图
  - `mapping_type_selected_summary.csv`: 课件/写作使用的分组摘要
- `inverse/`
  - `inverse_selected_summary.csv`
  - `inverse_selected_summary_table.svg`
- `symmetry/`
  - `symmetry_selected_summary.csv`
  - `symmetry_selected_summary_table.svg`
- `relation_frequency/`
  - `relation_frequency_selected_summary.csv`

## 当前建议

- `mapping type`：优先看 `with_table5_baseline/` 里的新版图
- `inverse / symmetry / relation frequency`：优先看各自 summary csv / table

## 口径提醒

- `mapping_type` 图中的红色线来自原论文 `Multiplicity/paper.pdf` 的 `Table 5`
- 这条线是 `FB15k-237 + without` 的 dataset-level 全局参考值
- 当前箱线图是 thesis 的 relation-level by-side 分布，因此红线应当理解为外部参考线，而不是完全同层级统计量
