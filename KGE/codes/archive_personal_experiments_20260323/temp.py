#!/usr/bin/python3

import numpy as np
import torch
import re
from math import pi
import os

# ======= 修改这些参数 =======
CHECKPOINT_PATH = "/data/satori_hdd1/EamonZhao/EamonFile/KGE/models/RotatE_FB15k-237_0/checkpoint"
RELATIONS_DICT_PATH = "/data/satori_hdd1/EamonZhao/EamonFile/KGE/data/relations.txt"
OUTPUT_CHECKPOINT_PATH = "/data/satori_hdd1/EamonZhao/EamonFile/KGE/models/RotatE_FB15k-237_0/checkpoint_shifted"
CATEGORIES_TO_SHIFT = ['film']
SHIFT_VALUE = -0.05
# ==========================

# 1. 加载checkpoint
checkpoint = torch.load(CHECKPOINT_PATH, map_location=torch.device('cpu'))
print(f"Checkpoint keys: {checkpoint.keys()}")
print(f"Model state dict keys: {checkpoint['model_state_dict'].keys()}")

# 2. 获取relation embedding
relation_embedding = checkpoint['model_state_dict']['relation_embedding']
print(f"Relation embedding shape: {relation_embedding.shape}")

# 3. 读取关系映射
relation_map = {}
with open(RELATIONS_DICT_PATH, 'r') as f:
    for line in f:
        idx, name = line.strip().split('\t')
        relation_map[int(idx)] = name

# 4. 找到要偏移的关系索引
indices_to_shift = []
for idx, name in relation_map.items():
    category = re.match(r'^/([^/]+)/', name)
    if category and category.group(1) in CATEGORIES_TO_SHIFT:
        indices_to_shift.append(idx)
        print(f"Will shift relation: {name} (index: {idx})")

# 5. 应用偏移
# 先将tensor转换为numpy，修改后再转回tensor
relation_embedding_np = relation_embedding.detach().numpy()
shifted_relation_embedding_np = relation_embedding_np.copy()

for idx in indices_to_shift:
    shifted_relation_embedding_np[idx] += SHIFT_VALUE * 0.011 * pi

# 转回tensor
shifted_relation_embedding = torch.from_numpy(shifted_relation_embedding_np).float()

# 6. 更新checkpoint中的relation embedding
checkpoint['model_state_dict']['relation_embedding'] = shifted_relation_embedding

# 7. 保存修改后的checkpoint
torch.save(checkpoint, OUTPUT_CHECKPOINT_PATH)

print(f"Shifted {len(indices_to_shift)} relations by {SHIFT_VALUE}")
print(f"Saved shifted checkpoint to: {OUTPUT_CHECKPOINT_PATH}")