import numpy as np
import torch
import argparse
import os
import random
from collections import defaultdict
import re
import json
import numpy as np

# 导入现有的模块
from model import KGEModel
from run import parse_args, read_triple

class RelationShiftAnalyzer:
    def __init__(self, checkpoint_path, data_path, gpu=-1):
        self.checkpoint_path = checkpoint_path
        self.data_path = data_path
        self.categories_to_relations = None
        self.model = None
        self.test_triples = None
        self.all_true_triples = None
        self.gpu = gpu

        self.target_categories = [
            'organization', 'education', 'people', 'film', 'tv', 
            'sports', 'award', 'music', 'location', 'base', 
            'government', 'olympics'
        ]
        
    def load_model_and_data(self):
        """加载模型和数据"""
        device = torch.device('cuda' if self.gpu >= 0 and torch.cuda.is_available() else 'cpu')
        # 加载模型checkpoint
        checkpoint = torch.load(self.checkpoint_path, map_location=torch.device('cpu'))

        args = argparse.Namespace()
        args.cuda = (self.gpu >= 0 and torch.cuda.is_available())

        # 加载配置文件
        config_path = os.path.join(os.path.dirname(self.checkpoint_path), 'config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # 从配置中获取参数
        args = argparse.Namespace()
        args.cuda = (self.gpu >= 0 and torch.cuda.is_available())
        args.data_path = self.data_path
        args.model = config['model']
        args.nentity = config['nentity']  
        args.nrelation = config['nrelation']
        args.hidden_dim = config['hidden_dim']
        args.gamma = config['gamma']
        args.double_entity_embedding = config['double_entity_embedding']
        args.double_relation_embedding = config['double_relation_embedding']
        # args.test_batch_size = config['test_batch_size']
        args.test_batch_size = 64
        args.countries = config.get('countries', False)
        args.cpu_num = 1
        args.test_log_steps = 1000
        
        # 创建模型实例
        self.model = KGEModel(
            model_name=args.model,
            nentity=args.nentity,
            nrelation=args.nrelation,
            hidden_dim=args.hidden_dim,
            gamma=args.gamma,
            double_entity_embedding=args.double_entity_embedding,
            double_relation_embedding=args.double_relation_embedding
        )
        self.model.load_state_dict(checkpoint['model_state_dict'])
        
        if args.cuda:
            self.model = self.model.cuda()

        # 使用run.py中的逻辑加载数据
        with open(os.path.join(self.data_path, 'entities.dict')) as fin:
            entity2id = dict()
            for line in fin:
                eid, entity = line.strip().split('\t')
                entity2id[entity] = int(eid)
        
        with open(os.path.join(self.data_path, 'relations.dict')) as fin:
            relation2id = dict()
            for line in fin:
                rid, relation = line.strip().split('\t')
                relation2id[relation] = int(rid)
        
        # 使用run.py中的read_triple函数
        self.test_triples = read_triple(os.path.join(self.data_path, 'test.txt'), entity2id, relation2id)
        train_triples = read_triple(os.path.join(self.data_path, 'train.txt'), entity2id, relation2id)
        valid_triples = read_triple(os.path.join(self.data_path, 'valid.txt'), entity2id, relation2id)
        self.all_true_triples = train_triples + valid_triples + self.test_triples
        
        # 保存args供后续使用
        self.args = args

        self.original_relation_embedding = self.model.relation_embedding.data.clone()
        
        print(f"成功加载模型和数据:")
        print(f"- 模型类型: {args.model}")
        print(f"- 实体数量: {args.nentity}")
        print(f"- 关系数量: {args.nrelation}")
        print(f"- 测试三元组数量: {len(self.test_triples)}")
            
    def load_relations(self, file_path):
        """加载关系文件，返回索引到关系名称的映射字典"""
        relation_map = {}
        with open(file_path, 'r') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    index, name = parts
                    relation_map[int(index)] = name
        return relation_map

    def extract_categories(self, relation_map):
        """从关系名称中提取类别，返回类别到关系索引列表的映射"""
        category_to_relations = defaultdict(list)
        
        for index, name in relation_map.items():
            # 使用正则表达式提取第一个和第二个斜杠之间的内容
            match = re.match(r'^/([^/]+)/', name)
            if match:
                category = match.group(1)
                category_to_relations[category].append(index)
        
        return category_to_relations

    def load_relation_categories(self):
        """加载关系分类"""
        relation_file = os.path.join(self.data_path, 'relations.dict')
        relation_map = self.load_relations(relation_file)
        self.categories_to_relations = self.extract_categories(relation_map)
        
        # 过滤出目标类别
        self.target_categories_to_relations = {}
        
        print(f"\n成功加载关系分类:")
        for category, relations in self.categories_to_relations.items():
            print(f"- {category}: {len(relations)} 个关系")
            
            # 如果是目标类别，添加到目标字典中
            if category in self.target_categories:
                self.target_categories_to_relations[category] = relations
        
        print(f"\n将进行偏移的类别:")
        for category, relations in self.target_categories_to_relations.items():
            print(f"- {category}: {len(relations)} 个关系")
        
        # 计算将被偏移的关系总数
        total_shift_relations = sum(len(relations) for relations in self.target_categories_to_relations.values())
        print(f"\n总共将有 {total_shift_relations} 个关系参与偏移")
        
        # 保存relation_map供后续使用
        self.relation_map = relation_map
        
        return self.categories_to_relations

    def apply_angle_shift(self, category_shifts):
        """
        应用角度偏移
        category_shifts: 字典，键为类别，值为偏移角度（弧度）
        """
        
        # 对每个目标类别应用偏移
        for category, shift_angle in category_shifts.items():
            if category not in self.target_categories_to_relations:
                continue
                
            relation_indices = self.target_categories_to_relations[category]
            
            # RotatE模型中关系表示为相位
            for idx in relation_indices:
                # 获取当前关系的嵌入
                current_embedding = self.model.relation_embedding.data[idx]
                
                # 将偏移角度应用到每个维度
                # RotatE中的关系表示是相位，直接添加偏移角度
                shifted_embedding = current_embedding + shift_angle * 0.011
                
                # 更新模型中的关系嵌入
                self.model.relation_embedding.data[idx] = shifted_embedding
        
        print(f"成功应用角度偏移:")
        for category, shift_angle in category_shifts.items():
            if category in self.target_categories_to_relations:
                print(f"- {category}: {shift_angle} 弧度")
        
    def evaluate(self):
        """评估模型性能"""
        # 调用现有的test_step函数
        metrics = KGEModel.test_step(self.model, self.test_triples, self.all_true_triples, self.args)
        
        # 打印评估结果
        print("\n评估结果:")
        for metric, value in metrics.items():
            print(f"- {metric}: {value:.4f}")
        
        return metrics
    
    def genetic_algorithm(self, 
                        population_size=20,
                        generations=50,
                        mutation_rate=0.1,
                        elite_ratio=0.1,
                        step_size=0.1):  # 默认1/10 pi
        """
        遗传算法主循环 - 离散角度偏移模型
        
        Args:
            population_size: 种群大小
            generations: 进化代数
            mutation_rate: 变异概率
            elite_ratio: 精英保留比例
            step_size: 角度步长（以π的倍数表示，如0.1表示0.1π）
        """

        
        # 定义离散值集合
        pi = np.pi
        steps = np.arange(-1.0, 1.0 + step_size/2, step_size)  # 从-π到π的系数
        self.angle_values = steps * pi  # 实际的弧度值
        
        print(f"\n开始遗传算法优化（离散模型）:")
        print(f"- 种群大小: {population_size}")
        print(f"- 进化代数: {generations}")
        print(f"- 变异率: {mutation_rate}")
        print(f"- 精英比例: {elite_ratio}")
        print(f"- 角度步长: {step_size}π")
        print(f"- 可选角度值: {len(self.angle_values)}个")
        print(f"- 角度范围: [{self.angle_values[0]/pi:.1f}π, {self.angle_values[-1]/pi:.1f}π]")
        
        # 计算原始模型性能作为基准
        print("\n评估原始模型性能...")
        original_metrics = self.evaluate()
        original_mrr = original_metrics['MRR']
        print(f"原始MRR: {original_mrr:.4f}")
        
        # 初始化种群（使用索引而不是实际值）
        population = self._initialize_discrete_population(population_size)
        
        # 评估初始种群
        fitness_scores = self._evaluate_discrete_population(population)
        
        # 记录最佳个体
        best_individual = None
        best_fitness = -float('inf')
        generation_stats = []
        
        # 进化循环
        for generation in range(generations):
            print(f"\n第 {generation+1}/{generations} 代:")
            
            # 选择
            parents = self._selection(population, fitness_scores)
            
            # 交叉
            offspring = self._discrete_crossover(parents, population_size)
            
            # 变异
            offspring = self._discrete_mutation(offspring, mutation_rate)
            
            # 精英保留
            elite_count = int(population_size * elite_ratio)
            elite_indices = np.argsort(fitness_scores)[-elite_count:]
            elites = [population[i] for i in elite_indices]
            
            # 组合新种群
            population = elites + offspring[:(population_size - elite_count)]
            
            # 评估新种群
            fitness_scores = self._evaluate_discrete_population(population)
            
            # 记录本代最佳个体
            gen_best_idx = np.argmax(fitness_scores)
            gen_best_fitness = fitness_scores[gen_best_idx]
            gen_best_individual = population[gen_best_idx]
            
            if gen_best_fitness > best_fitness:
                best_fitness = gen_best_fitness
                best_individual = gen_best_individual.copy()
            
            # 记录统计信息
            stats = {
                'generation': generation + 1,
                'best_fitness': best_fitness,
                'gen_best_fitness': gen_best_fitness,
                'avg_fitness': np.mean(fitness_scores),
                'improvement': best_fitness - original_mrr
            }
            generation_stats.append(stats)
            
            print(f"- 本代最佳MRR: {gen_best_fitness:.4f}")
            print(f"- 历史最佳MRR: {best_fitness:.4f}")
            print(f"- 平均MRR: {stats['avg_fitness']:.4f}")
            print(f"- 相比原始提升: {stats['improvement']:.4f}")
        
        # 将索引转换回角度值
        best_angles = [self.angle_values[idx] for idx in best_individual]
        
        # 返回最优解
        print("\n遗传算法优化完成!")
        print(f"最佳偏移方案:")
        best_shifts = {
            category: best_angles[i] 
            for i, category in enumerate(self.target_categories)
        }
        for category, shift in best_shifts.items():
            print(f"- {category}: {shift/np.pi:.2f}π ({shift:.4f}弧度)")
        
        return best_angles, best_fitness, generation_stats

    def _initialize_discrete_population(self, size):
        """初始化离散种群（使用索引）- 按照离散高斯分布"""
        population = []
        
        # 计算每个离散点的概率（高斯分布）
        center_idx = len(self.angle_values) // 2  # 中心索引（对应0°）
        sigma = len(self.angle_values) / 6  # 标准差，约6σ覆盖整个范围
        
        # 计算每个索引的概率
        probabilities = []
        for i in range(len(self.angle_values)):
            # 高斯分布公式
            prob = np.exp(-((i - center_idx) ** 2) / (2 * sigma ** 2))
            probabilities.append(prob)
        
        # 归一化概率
        probabilities = np.array(probabilities)
        probabilities = probabilities / probabilities.sum()
        
        # 根据概率生成种群
        for _ in range(size):
            # 对每个类别，按概率选择角度索引
            individual = np.random.choice(
                len(self.angle_values), 
                size=len(self.target_categories),
                p=probabilities
            )
            population.append(individual)
        
        return population

    def _evaluate_discrete_population(self, population):
        """评估离散种群中每个个体的适应度"""
        fitness_scores = []
        
        for i, individual in enumerate(population):
            # 将索引转换为实际角度值
            angles = [self.angle_values[idx] for idx in individual]
            
            # 将个体转换为偏移字典
            shifts = {
                category: angles[j] 
                for j, category in enumerate(self.target_categories)
            }
            
            # 应用偏移
            self.apply_angle_shift(shifts)
            
            # 评估
            metrics = self.evaluate()
            fitness = metrics['MRR']  # 使用MRR作为适应度
            fitness_scores.append(fitness)
            
            # 恢复原始嵌入
            self.model.relation_embedding.data = self.original_relation_embedding.clone()
            
            print(f"个体 {i+1}/{len(population)} - MRR: {fitness:.4f}")
        
        return fitness_scores

    def _discrete_crossover(self, parents, offspring_size):
        """离散交叉操作 - 使用单点交叉"""
        offspring = []
        
        for i in range(0, offspring_size, 2):
            parent1 = parents[i % len(parents)]
            parent2 = parents[(i + 1) % len(parents)]
            
            if i + 1 < offspring_size:
                # 随机选择交叉点
                crossover_point = np.random.randint(1, len(parent1))
                
                # 创建两个子代
                child1 = np.concatenate([parent1[:crossover_point], parent2[crossover_point:]])
                child2 = np.concatenate([parent2[:crossover_point], parent1[crossover_point:]])
                
                offspring.extend([child1, child2])
            else:
                offspring.append(parent1.copy())
        
        return offspring

    def _discrete_mutation(self, offspring, mutation_rate):
        """离散变异操作"""
        for individual in offspring:
            for i in range(len(individual)):
                if np.random.random() < mutation_rate:
                    # 随机选择一个新的索引
                    individual[i] = np.random.randint(0, len(self.angle_values))
        
        return offspring

    def _selection(self, population, fitness_scores):
        """选择操作 - 使用轮盘赌选择"""
        # 将适应度转换为概率
        fitness_array = np.array(fitness_scores)
        min_fitness = np.min(fitness_array)
        
        # 处理负值情况
        if min_fitness < 0:
            fitness_array = fitness_array - min_fitness
        
        # 归一化
        fitness_sum = np.sum(fitness_array)
        if fitness_sum == 0:
            probabilities = np.ones(len(population)) / len(population)
        else:
            probabilities = fitness_array / fitness_sum
        
        # 选择父代
        parent_indices = np.random.choice(
            len(population), 
            size=len(population), 
            p=probabilities,
            replace=True
        )
        
        return [population[i] for i in parent_indices]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint_path', type=str, required=True)
    parser.add_argument('--data_path', type=str, required=True)
    parser.add_argument('--gpu', type=int, default=-1, help='GPU编号，-1表示使用CPU')
    args = parser.parse_args()

    # 设置GPU
    if args.gpu >= 0:
        os.environ['CUDA_VISIBLE_DEVICES'] = str(args.gpu)
    
    analyzer = RelationShiftAnalyzer(args.checkpoint_path, args.data_path, args.gpu)
    analyzer.load_model_and_data()
    analyzer.load_relation_categories()
    
    # 直接运行遗传算法
    best_angles, best_fitness, stats = analyzer.genetic_algorithm(
        population_size=20,
        generations=50,
        mutation_rate=0.1,
        elite_ratio=0.1,
        step_size=0.1  # 1/10 π
    )
    
    # 保存结果
    with open('genetic_algorithm_results.json', 'w') as f:
        json.dump({
            'best_individual': [float(angle) for angle in best_angles],  
            'best_fitness': float(best_fitness),
            'stats': stats
        }, f, indent=2)