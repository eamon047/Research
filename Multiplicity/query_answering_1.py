#%%
import os
import re
import torch
import pickle
import math
import random
import argparse
from tqdm import tqdm
import pickle
import logging
from kge import Dataset
from kge.job import Job
from kge import Config
from argparse import Namespace
from torch.utils.data import DataLoader
from itertools import combinations
from scipy.stats import kendalltau

from kge.util.seed import seed_from_config
from kge.util.io import get_checkpoint_file, load_checkpoint
#%%
def get_top10(scores):
    """
    get sorted top 10 entity IDs for each query.
    """
    _, top10 = torch.topk(scores, k=10, dim=1)
    return top10

def without_aggregation(score_paths):
    scores = torch.load(score_paths[-1])
    return scores

def majority_aggregation(score_paths):
    scores = torch.load(score_paths[0])
    total_samples = scores.shape[0]
    agg_scores = []
    for i in tqdm(range(0, total_samples, batch_size)):
        score_tensor = []
        for score_path in score_paths:
            scores = torch.load(score_path)
            score_tensor.append(scores[i:i+batch_size, :])
        # aggregate scores
        score_tensor = torch.stack(score_tensor, dim=2).cuda()
         # average aggregation here
        _, max_indices = torch.max(score_tensor, dim=1, keepdim=True)
        trunk_scores = torch.zeros_like(score_tensor)
        trunk_scores.scatter_(dim=1, index=max_indices, value=1)
        trunk_scores = torch.mean(trunk_scores, dim=2)
        agg_scores.append(trunk_scores.cpu())
    return torch.cat(agg_scores)

def borda_aggregation(score_paths):
    def borda_scores(scores):
        """
        input: scores of multiple checkpoints (#batch*#entity*#rep)
        output: aggregated scores with voting scores
        """
        _, num_entities, _ = scores.shape
        sorted_indices = torch.argsort(scores, dim=1)
        range_tensor = torch.arange(1, num_entities + 1, device = scores.device, dtype=scores.dtype).view(1, -1, 1)
        borda_scores = torch.zeros_like(scores)
        borda_scores.scatter_(1, sorted_indices, range_tensor.expand_as(sorted_indices))
        sum_borda_scores = torch.sum(borda_scores, dim=2)
        return sum_borda_scores

    scores = torch.load(score_paths[0])
    total_samples = scores.shape[0]
    #batch_size = 200

    agg_scores = []
    for i in tqdm(range(0, total_samples, batch_size)):
        score_tensor = []
        for score_path in score_paths:
            scores = torch.load(score_path)
            score_tensor.append(scores[i:i+batch_size, :])
        # aggregate scores
        score_tensor = torch.stack(score_tensor, dim=2).cuda()
        trunk_scores = borda_scores(score_tensor)
        agg_scores.append(trunk_scores.cpu())
    return torch.cat(agg_scores)

def average_aggregation(score_paths):
    scores = torch.load(score_paths[0])
    total_samples = scores.shape[0]
    #batch_size = 200

    agg_scores = []
    for i in tqdm(range(0, total_samples, batch_size)):
        score_tensor = []
        for score_path in score_paths:
            scores = torch.load(score_path)
            score_tensor.append(scores[i:i+batch_size, :]*random.randint(0, 1000))
        # aggregate scores
        score_tensor = torch.stack(score_tensor, dim=2).cuda()
         # average aggregation here
        trunk_scores = torch.mean(score_tensor, dim=2)
        agg_scores.append(trunk_scores.cpu())
    return torch.cat(agg_scores)

def norm_aggregation(score_paths):
    scores = torch.load(score_paths[0])
    total_samples = scores.shape[0]
    #batch_size = 200

    agg_scores = []
    for i in tqdm(range(0, total_samples, batch_size)):
        score_tensor = []
        for score_path in score_paths:
            scores = torch.load(score_path)
            min_score = torch.min(scores)
            max_score = torch.max(scores)
            norm_scores = (scores[i:i+batch_size, :] - min_score)/(max_score-min_score)
            score_tensor.append(norm_scores)
        # aggregate scores
        score_tensor = torch.stack(score_tensor, dim=2).cuda()
         # average aggregation here
        trunk_scores = torch.mean(score_tensor, dim=2)
        agg_scores.append(trunk_scores.cpu())
    return torch.cat(agg_scores)

def calc_performance(o_scores, s_scores, mask, mn_mask, dataset):
    """
    note o_ranks and s_ranks should be 
    the ranks for testing triples
    the dimension should be #queries*1
    """
    def hits(hits):
        return (torch.sum(hits)/len(hits)).item()
    def mr(ranks):
        return torch.mean(ranks).item()
    def mrr(ranks):
        return torch.mean(torch.reciprocal(ranks)).item()
    def overall(h, mask):
        return ((h["1_1_head"]*sum(mask["1-1"]) + \
                    h["1_N_head"]*sum(mask["1-N"]) + \
                    h["1_1_tail"]*sum(mask["1-1"]) + \
                    h["M_1_tail"]*sum(mask["M-1"])) / \
                (sum(mask["1-1"])*2 + \
                    sum(mask["1-N"]) + \
                    sum(mask["M-1"]))).item()
    def score2rank(o_scores, s_scores):
        lookup = dict(
            WN18 = "/home/zyh7abt/kge/data/wn18", 
            WN18RR = "/home/zyh7abt/kge/data/wnrr",
            FB15k237 = "/home/zyh7abt/kge/data/fb15k-237",
            FB15k = "/home/zyh7abt/kge/data/fb15k",
            YAGO3 = "/home/zyh7abt/kge/data/yago3-10"
            )
        
        dataset_path = lookup[dataset]
        filename = os.path.join(dataset_path, "test.del")
        with open(filename, 'r') as file:
            test_triples = []
            for line in file:
                test_triples.append(line.rstrip('\n'))
        s = torch.Tensor([int(triple.split("\t")[0]) for triple in test_triples]).long()
        o = torch.Tensor([int(triple.split("\t")[2]) for triple in test_triples]).long()

        # get ranks (filter m-n relations)
        o_pred_score = o_scores[range(o_scores.shape[0]), o[~mn_mask]]
        s_pred_score = s_scores[range(s_scores.shape[0]), s[~mn_mask]]

        o_pred_ranks = torch.sum(o_scores>=o_pred_score.unsqueeze(1), dim=1).to(torch.float32)
        s_pred_ranks = torch.sum(s_scores>=s_pred_score.unsqueeze(1), dim=1).to(torch.float32)

        return o_pred_ranks, s_pred_ranks

    # convert scores to ranks
    o_ranks, s_ranks = score2rank(o_scores, s_scores)

    performance_dict = dict()
    # evaluate MR
    h = dict()
    h["1_1_head"] = mr(s_ranks[mask["1-1"]])
    h["1_N_head"] = mr(s_ranks[mask["1-N"]])
    h["1_1_tail"] = mr(o_ranks[mask["1-1"]])
    h["M_1_tail"] = mr(o_ranks[mask["M-1"]])
    h["overall"] = overall(h, mask)
    performance_dict["mr"] = h

    # evaluate MRR
    h = dict()
    h["1_1_head"] = mrr(s_ranks[mask["1-1"]])
    h["1_N_head"] = mrr(s_ranks[mask["1-N"]])
    h["1_1_tail"] = mrr(o_ranks[mask["1-1"]])
    h["M_1_tail"] = mrr(o_ranks[mask["M-1"]])
    h["overall"] = overall(h, mask)
    performance_dict["mrr"] = h

    # evaluate hits@k
    for k in [1,3,10]:
        o_hits = o_ranks <= k
        s_hits = s_ranks <= k
        # filter
        h = dict()
        h["1_1_head"] = hits(s_hits[mask["1-1"]])
        h["1_N_head"] = hits(s_hits[mask["1-N"]])
        h["1_1_tail"] = hits(o_hits[mask["1-1"]])
        h["M_1_tail"] = hits(o_hits[mask["M-1"]])
        h["overall"] = overall(h, mask)
        performance_dict[f"hits@{k}"] = h
    return performance_dict

def retrieve_performance(performance_list):
    performance_dict = performance_list[0].copy()
    for metric in ["mr", "mrr", "hits@1", "hits@3", "hits@10"]:
        for type in ["1_1_head", "1_N_head", "1_1_tail", "M_1_tail", "overall"]:
            l = [perform_dict[metric][type] for perform_dict in performance_list]
            performance_dict[metric][type] = sum(l)/len(l)
    return performance_dict

def calc_multiplicity(o_tensor, s_tensor, mask):
    def calc_ambiguity(tensor, k, mask):
        tensor = torch.stack(tensor, dim=2)
        tensor = tensor[mask,:,:]
        count = 0
        for i in range(tensor.shape[0]):
            eval_tensor = tensor[i,:k, :]
            sets_list = [set(eval_tensor[:,n].tolist()) for n in range(eval_tensor.shape[1])]
            if all(s == sets_list[0] for s in sets_list):
                count += 1
        return (tensor.shape[0] - count)/tensor.shape[0]

    def calc_discrepancy(tensor, k, mask):
        ambiguity = []
        for tensor_1, tensor_2 in combinations(tensor, 2):
            ambiguity.append(calc_ambiguity([tensor_1, tensor_2], k, mask))

        return max(ambiguity)

    def overall(h, mask):
        return ((h["1_1_head"]*sum(mask["1-1"]) + \
                    h["1_N_head"]*sum(mask["1-N"]) + \
                    h["1_1_tail"]*sum(mask["1-1"]) + \
                    h["M_1_tail"]*sum(mask["M-1"])) / \
                (sum(mask["1-1"])*2 + \
                    sum(mask["1-N"]) + \
                    sum(mask["M-1"]))).item()
    
    multiplicity_dict = dict()
    # ealuate ambiguity
    h = dict()
    h["1_1_head"] = calc_ambiguity(s_tensor, 1, mask["1-1"])
    h["1_N_head"] = calc_ambiguity(s_tensor, 1, mask["1-N"])
    h["1_1_tail"] = calc_ambiguity(o_tensor, 1, mask["1-1"])
    h["M_1_tail"] = calc_ambiguity(o_tensor, 1, mask["M-1"])
    h["overall"] = overall(h, mask)
    multiplicity_dict[f"ambiguity"] = h

    # evaluate discrepancy
    h = dict()
    h["1_1_head"] = calc_discrepancy(s_tensor, 1, mask["1-1"])
    h["1_N_head"] = calc_discrepancy(s_tensor, 1, mask["1-N"])
    h["1_1_tail"] = calc_discrepancy(o_tensor, 1, mask["1-1"])
    h["M_1_tail"] = calc_discrepancy(o_tensor, 1, mask["M-1"])
    h["overall"] = overall(h, mask)
    multiplicity_dict[f"discrepancy"] = h

    return multiplicity_dict

def evaluation(model, dataset, aggregation_func, args):
    # retrieve settings
    num = int(args.num)
    agg_num = int(args.agg)
    random_seed = int(args.seed)

    # specify relevant dir
    result_dir = os.path.join("/fs/scratch/rb_bd_dlp_rng_dl01_cr_ICT_employees/zyh7abt/finished", f"{model}/{model}_{dataset}")
    result_list = [name for name in os.listdir(result_dir) if os.path.isdir(os.path.join(result_dir, name))]
    score_dir = os.path.join("/fs/scratch/rb_bd_dlp_rng_dl01_cr_ICT_employees/zyh7abt/filtered_scores", f"{model}/{model}_{dataset}")

    # select results to be evaluated
    random.seed(random_seed)
    select_results = random.sample(result_list, num)
    rep_path_list = []
    for select_result in select_results:
        agg_results = random.sample([x for x in result_list if x != select_result], agg_num-1)
        agg_results.append(select_result)
        rep_path_list.append(agg_results)

    # load relation mask
    mask_path = os.path.join(score_dir, "relation_mask.pkl")
    with open(mask_path, 'rb') as file:
        rel_mask = pickle.load(file)
    # load M-N relation mask
    mn_mask = torch.load(os.path.join(score_dir, "MN_mask.pt"))

    o_tensor, s_tensor = [], []
    performance_list = []
    for agg_path_list in rep_path_list:
        # get score paths for aggregation
        o_score_paths, s_score_paths = [], []
        for agg_path in agg_path_list:
            # get paths
            o_score_path = os.path.join(score_dir, f"{agg_path}_o.pt")
            s_score_path = os.path.join(score_dir, f"{agg_path}_s.pt")
            o_score_paths.append(o_score_path)
            s_score_paths.append(s_score_path)
        
        # aggregate the scores
        o_agg_scores = aggregation_func(o_score_paths)
        s_agg_scores = aggregation_func(s_score_paths)
        
        # performance evaluation
        performance_list.append(calc_performance(o_agg_scores, s_agg_scores, rel_mask, mn_mask, dataset))

        o_tensor.append(get_top10(o_agg_scores))
        s_tensor.append(get_top10(o_agg_scores))
    
    # evaluate performance
    performance_dict = retrieve_performance(performance_list)

    # evaluate multiplicity
    multiplicity_dict = calc_multiplicity(o_tensor, s_tensor, rel_mask)

    return performance_dict, multiplicity_dict

def print_performance(performance_dict):
    logging.info(f"\t performance: ")
    for metric in ["mr", "mrr", "hits@1", "hits@3", "hits@10"]:
        out_str = f"\t {metric}: "
        out_str += f"{performance_dict[metric]['overall']:.3f} "
        out_str += f"({performance_dict[metric]['1_1_head']:.3f}/"
        out_str += f"{performance_dict[metric]['1_N_head']:.3f}/"
        out_str += f"{performance_dict[metric]['1_1_tail']:.3f}/"
        out_str += f"{performance_dict[metric]['M_1_tail']:.3f})"
        logging.info(out_str)

def print_multiplicity(multiplicity_dict):
    logging.info(f"\t multiplicity: ")
    for metric in ["ambiguity", "discrepancy"]:
        out_str = f"\t {metric}: "
        out_str += f"{multiplicity_dict[metric]['overall']:.3f} "
        out_str += f"({multiplicity_dict[metric]['1_1_head']:.3f}/"
        out_str += f"{multiplicity_dict[metric]['1_N_head']:.3f}/"
        out_str += f"{multiplicity_dict[metric]['1_1_tail']:.3f}/"
        out_str += f"{multiplicity_dict[metric]['M_1_tail']:.3f})"
        logging.info(out_str)

def batch_evaluation():
    parser = argparse.ArgumentParser(description='evaluate single model.')
    parser.add_argument('-num', '--num', help='number of repetition', default=2)
    parser.add_argument('-agg', '--agg', help='number of aggregation', default=2)
    parser.add_argument('-seed', '--seed', help='random seed', default=0)
    args = parser.parse_args()

    model_list = ["TransE", "RotatE", "ComplEx", "RESCAL", "DistMult", "ConvE"]
    dataset_list = ["WN18", "WN18RR", "FB15k237", "FB15k"]

    # save_name = f"local/rep{settings['num']}_agg{settings['agg_num']}_random{settings['random_seed']}"
    save_name = f"local/multi_rep{args.num}_agg{args.agg}_random{args.seed}"

    # file logger
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
        filename=f"{save_name}.log"
    )
    # stdout logger
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)
    logging.info("Saving logs in: {}".format(save_name))

    # dict initialization
    result_dict = {}
    for model in model_list:
        result_dict[model] = {}
        for dataset in dataset_list:
            result_dict[model][dataset] = {}
            for agg_method in ["without", "major", "borda", "average", "norm"]:
                result_dict[model][dataset][agg_method] = {}
                for eval_type in ["performance", "robustness"]:
                    result_dict[model][dataset][agg_method][eval_type] = {}
    # evaluation
    for model in model_list:
        for dataset in dataset_list:
            logging.info(f"{model}_{dataset}:")
            performance_dict, robustness_dict = evaluation(model, dataset, without_aggregation, args)
            logging.info(f" --------------- without aggregation --------------- ")
            print_performance(performance_dict)
            print_multiplicity(robustness_dict)
            result_dict[model][dataset]["without"]["performance"] = performance_dict
            result_dict[model][dataset]["without"]["robustness"] = robustness_dict

            performance_dict, robustness_dict = evaluation(model, dataset, majority_aggregation, args)
            logging.info(f" --------------- majority aggregation --------------- ")
            print_performance(performance_dict)
            print_multiplicity(robustness_dict)
            result_dict[model][dataset]["major"]["performance"] = performance_dict
            result_dict[model][dataset]["major"]["robustness"] = robustness_dict

            performance_dict, robustness_dict = evaluation(model, dataset, borda_aggregation, args)
            logging.info(f" --------------- borda aggregation --------------- ")
            print_performance(performance_dict)
            print_multiplicity(robustness_dict)
            result_dict[model][dataset]["borda"]["performance"] = performance_dict
            result_dict[model][dataset]["borda"]["robustness"] = robustness_dict

            performance_dict, robustness_dict = evaluation(model, dataset, average_aggregation, args)
            logging.info(f" --------------- average aggregation --------------- ")
            print_performance(performance_dict)
            print_multiplicity(robustness_dict)
            result_dict[model][dataset]["average"]["performance"] = performance_dict
            result_dict[model][dataset]["average"]["robustness"] = robustness_dict

            performance_dict, robustness_dict = evaluation(model, dataset, norm_aggregation, args)
            logging.info(f" --------------- norm aggregation --------------- ")
            print_performance(performance_dict)
            print_multiplicity(robustness_dict)
            result_dict[model][dataset]["norm"]["performance"] = performance_dict
            result_dict[model][dataset]["norm"]["robustness"] = robustness_dict

            logging.info(f" ----------------------------------------------- ")

    with open(f'{save_name}.pkl', 'wb') as pickle_file:
        pickle.dump(result_dict, pickle_file)
#%%
if __name__ == "__main__":
    batch_size = 200
    # single_evaluation()
    batch_evaluation()

# %%
