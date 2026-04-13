# %%
# This is the script to evaluate predictive multiplicity for link prediction
# with a fixed rank threshold.
import argparse
import os
import random
from collections import defaultdict

import pandas as pd
import torch
import torch.nn.functional as F

import kge.job
from kge import Config
from kge import Dataset
from kge.job import Job
from kge.util.dump import add_dump_parsers
from kge.util.io import get_checkpoint_file, load_checkpoint
from kge.util.package import add_package_parser
from kge.util.seed import seed_from_config


def argparse_bool_type(v):
    "Type for argparse that correctly treats Boolean values"
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def process_meta_command(args, meta_command, fixed_args):
    """Process and update program arguments for meta commands."""
    if args.command == meta_command:
        for k, v in fixed_args.items():
            if k != "command" and vars(args)[k] and vars(args)[k] != v:
                raise ValueError(
                    "invalid argument for '{}' command: --{} {}".format(
                        meta_command, k, v
                    )
                )
            vars(args)[k] = v


def create_parser(config, additional_args=None):
    if additional_args is None:
        additional_args = []

    short_options = {
        "dataset.name": "-d",
        "job.type": "-j",
        "train.max_epochs": "-e",
        "model": "-m",
    }

    parser_conf = argparse.ArgumentParser(add_help=False)
    for key, value in Config.flatten(config.options).items():
        short = short_options.get(key)
        argtype = type(value)
        if argtype == bool:
            argtype = argparse_bool_type
        if short:
            parser_conf.add_argument("--" + key, short, type=argtype)
        else:
            parser_conf.add_argument("--" + key, type=argtype)

    for key in additional_args:
        parser_conf.add_argument(key)

    parser_conf.add_argument(
        "--abort-when-cache-outdated",
        action="store_const",
        const=True,
        default=False,
        help=(
            "Abort processing when an outdated cached dataset file is found. "
            "Default is to recompute such cache files."
        ),
    )

    parser = argparse.ArgumentParser("kge")
    subparsers = parser.add_subparsers(title="command", dest="command")
    subparsers.required = True

    parser_start = subparsers.add_parser(
        "start", help="Start a new job (create and run it)", parents=[parser_conf]
    )
    parser_create = subparsers.add_parser(
        "create", help="Create a new job (but do not run it)", parents=[parser_conf]
    )
    for p in [parser_start, parser_create]:
        p.add_argument("config", type=str, nargs="?")
        p.add_argument("--folder", "-f", type=str, help="Output folder to use")
        p.add_argument(
            "--run",
            default=p is parser_start,
            type=argparse_bool_type,
            help="Whether to immediately run the created job",
        )

    parser_resume = subparsers.add_parser(
        "resume", help="Resume a prior job", parents=[parser_conf]
    )
    parser_eval = subparsers.add_parser(
        "eval", help="Evaluate the result of a prior job", parents=[parser_conf]
    )
    parser_valid = subparsers.add_parser(
        "valid",
        help="Evaluate the result of a prior job using validation data",
        parents=[parser_conf],
    )
    parser_test = subparsers.add_parser(
        "test",
        help="Evaluate the result of a prior job using test data",
        parents=[parser_conf],
    )
    for p in [parser_resume, parser_eval, parser_valid, parser_test]:
        p.add_argument("config", type=str)
        p.add_argument(
            "--checkpoint",
            type=str,
            help=(
                "Which checkpoint to use: 'default', 'last', 'best', a number "
                "or a file name"
            ),
            default="default",
        )

    add_dump_parsers(subparsers)
    add_package_parser(subparsers)
    return parser


def get_job(folder):
    cmd = ["test", folder]
    config = Config()
    parser = create_parser(config)
    args, _unknown_args = parser.parse_known_args(cmd)

    process_meta_command(args, "create", {"command": "start", "run": False})
    process_meta_command(args, "eval", {"command": "resume", "job.type": "eval"})
    process_meta_command(
        args, "test", {"command": "resume", "job.type": "eval", "eval.split": "test"}
    )
    process_meta_command(
        args,
        "valid",
        {"command": "resume", "job.type": "eval", "eval.split": "valid"},
    )

    if args.command == "resume":
        if os.path.isdir(args.config) and os.path.isfile(args.config + "/config.yaml"):
            args.config += "/config.yaml"
        if not vars(args)["console.quiet"]:
            print("Resuming from configuration {}...".format(args.config))
        config.load(args.config)
        config.folder = os.path.dirname(args.config)
        if not config.folder:
            config.folder = "."
        if not os.path.exists(config.folder):
            raise ValueError(
                "{} is not a valid config file for resuming".format(args.config)
            )

    # Use a smaller evaluation batch to reduce GPU memory pressure during
    # multiplicity evaluation. This changes runtime, not the evaluation logic.
    config.set("eval.batch_size", 16)

    for key, value in vars(args).items():
        if key in [
            "command",
            "config",
            "run",
            "folder",
            "checkpoint",
            "abort_when_cache_outdated",
        ]:
            continue
        if value is not None:
            if key == "search.device_pool":
                value = "".join(value).split(",")
            try:
                if isinstance(config.get(key), bool):
                    value = argparse_bool_type(value)
            except KeyError:
                pass
            config.set(key, value)
            if key == "model":
                config._import(value)

    checkpoint_file = get_checkpoint_file(config, args.checkpoint)
    Dataset._abort_when_cache_outdated = args.abort_when_cache_outdated
    seed_from_config(config)
    dataset = Dataset.create(config)
    checkpoint = load_checkpoint(checkpoint_file, config.get("job.device"))
    job = Job.create_from(checkpoint, new_config=config, dataset=dataset)

    if not job._is_prepared:
        job._prepare()
        job._is_prepared = True

    for f in job.pre_run_hooks:
        f(job)

    return job


def majority_scoring(scores):
    max_indices = torch.argmax(scores, dim=1)
    return F.one_hot(max_indices, num_classes=scores.shape[1])


def borda_scoring(scores):
    _, indices = torch.sort(scores, descending=True, dim=1)
    borda_scores = torch.arange(scores.shape[1] - 1, -1, -1).expand_as(scores).cuda()
    return torch.zeros_like(scores, dtype=borda_scores.dtype).scatter_(
        1, indices, borda_scores
    )


def range_scoring(scores):
    min_score = torch.min(scores)
    max_score = torch.max(scores)
    return 2 * (scores - min_score) / (max_score - min_score) - 1


def compute_ranks(jobs, agg_func=None):
    num_entities = jobs[0].dataset.num_entities()
    device = jobs[0].device
    loader = jobs[0].loader
    labels_for_ranking = defaultdict(lambda: None)
    s_ranks = []
    o_ranks = []

    for _batch_number, batch_coords in enumerate(loader):
        batch = batch_coords[0].to(device)
        s, p, o = batch[:, 0], batch[:, 1], batch[:, 2]
        label_coords = batch_coords[1].to(device)

        labels = kge.job.util.coord_to_sparse_tensor(
            len(batch), 2 * num_entities, label_coords, device, float("Inf")
        )
        labels_for_ranking["_filt"] = labels

        scores_sp = torch.zeros([batch.shape[0], num_entities], device=device)
        scores_po = torch.zeros([batch.shape[0], num_entities], device=device)
        with torch.no_grad():
            if agg_func is None:
                scores = jobs[-1].model.score_sp_po(s, p, o)
                scores_sp = scores[:, :num_entities]
                scores_po = scores[:, num_entities:]
            else:
                for job in jobs:
                    scores = job.model.score_sp_po(s, p, o)
                    scores_sp += agg_func(scores[:, :num_entities])
                    scores_po += agg_func(scores[:, num_entities:])

        o_true_scores = scores_sp[range(o.shape[0]), o]
        s_true_scores = scores_po[range(s.shape[0]), s]

        ranks_and_ties_for_ranking = defaultdict(
            lambda: [
                torch.zeros(s.size(0), dtype=torch.long, device=device),
                torch.zeros(s.size(0), dtype=torch.long, device=device),
            ]
        )

        chunk_start = 0
        chunk_end = num_entities
        labels_chunk = jobs[0]._densify_chunk_of_labels(
            labels_for_ranking["_filt"], chunk_start, chunk_end
        )

        s_in_chunk_mask = (chunk_start <= s) & (s < chunk_end)
        o_in_chunk_mask = (chunk_start <= o) & (o < chunk_end)
        o_in_chunk = (o[o_in_chunk_mask] - chunk_start).long()
        s_in_chunk = (s[s_in_chunk_mask] - chunk_start).long()

        labels_chunk[o_in_chunk_mask, o_in_chunk] = 0
        labels_chunk[
            s_in_chunk_mask, s_in_chunk + (chunk_end - chunk_start)
        ] = 0

        (
            s_rank_chunk,
            s_num_ties_chunk,
            o_rank_chunk,
            o_num_ties_chunk,
            scores_sp_filt,
            scores_po_filt,
        ) = jobs[0]._filter_and_rank(
            scores_sp, scores_po, labels_chunk, o_true_scores, s_true_scores
        )

        scores_sp = scores_sp_filt
        scores_po = scores_po_filt

        ranks_and_ties_for_ranking["s_filt"][0] += s_rank_chunk
        ranks_and_ties_for_ranking["s_filt"][1] += s_num_ties_chunk
        ranks_and_ties_for_ranking["o_filt"][0] += o_rank_chunk
        ranks_and_ties_for_ranking["o_filt"][1] += o_num_ties_chunk

        s_rank = jobs[0]._get_ranks(
            ranks_and_ties_for_ranking["s_filt"][0],
            ranks_and_ties_for_ranking["s_filt"][1],
        )
        o_rank = jobs[0]._get_ranks(
            ranks_and_ties_for_ranking["o_filt"][0],
            ranks_and_ties_for_ranking["o_filt"][1],
        )
        s_ranks.append(s_rank)
        o_ranks.append(o_rank)

    s_ranks = torch.cat(s_ranks)
    o_ranks = torch.cat(o_ranks)
    return s_ranks, o_ranks


def hits_at_k(ranks, k):
    hits = torch.sum(ranks < k) / ranks.shape[0]
    return hits.item()


def ambiguity_at_k(ranks, k):
    hits_tensor = torch.stack(ranks) < k
    true_count = torch.sum(hits_tensor, dim=0)
    amb_bool = (true_count > 0) & (true_count < hits_tensor.shape[0])
    ambiguity = torch.sum(amb_bool) / amb_bool.shape[0]
    return ambiguity.item()


def discrepancy_at_k(ranks, k):
    baseline = ranks[0] < k
    discrepancy = 0
    for rank in ranks[1:]:
        competing = rank < k
        candidate = torch.sum(baseline != competing).item()
        if candidate > discrepancy:
            discrepancy = candidate
    return discrepancy / baseline.shape[0]


def evaluation(jobs, agg_index_list, k, agg_func=None):
    ranks = []
    for agg_indices in agg_index_list:
        agg_jobs = [jobs[i] for i in agg_indices]
        if agg_func is None:
            s_ranks, o_ranks = compute_ranks(agg_jobs)
        else:
            s_ranks, o_ranks = compute_ranks(agg_jobs, agg_func=agg_func)
        ranks.append(torch.cat([s_ranks, o_ranks]))

    mask = torch.any(torch.stack(ranks) < k, dim=0)
    masked_ranks = []
    for rank in ranks:
        masked_ranks.append(rank[mask])

    hits = []
    for rank in ranks:
        hits.append(hits_at_k(rank, k))

    mean_hits = sum(hits) / len(hits)
    epsilon = max(hits) - min(hits)
    ambiguity = ambiguity_at_k(masked_ranks, k)
    discrepancy = discrepancy_at_k(masked_ranks, k)
    return mean_hits, epsilon, ambiguity, discrepancy


def run_experiment():
    # Minimal local configuration.
    # For TransE_N, set EXPERIMENT_NAME = "TransE_FB15k237_N".
    EXPERIMENTS_ROOT = "LibKGE/local/multiplicity"
    MODEL = "RotatE"
    DATASET = "FB15k237"
    EXPERIMENT_NAME = "RotatE_FB15k237"

    NUM = 7
    AGG_NUM = 7
    K = 10
    RANDOM_SEED = 0

    OUTPUT_CSV = "results/RotatE_FB15k237_num7_agg7_k10.csv"

    experiment_dir = os.path.join(EXPERIMENTS_ROOT, EXPERIMENT_NAME)
    print(f"{MODEL}-{DATASET}")
    print(f"Loading runs from: {experiment_dir}")

    if not os.path.isdir(experiment_dir):
        raise FileNotFoundError(f"Experiment directory does not exist: {experiment_dir}")

    dir_paths = [
        os.path.join(experiment_dir, name)
        for name in sorted(os.listdir(experiment_dir))
        if os.path.isdir(os.path.join(experiment_dir, name))
        and os.path.isfile(os.path.join(experiment_dir, name, "config.yaml"))
    ]

    if len(dir_paths) < NUM:
        raise ValueError(
            f"Need at least {NUM} runs, but only found {len(dir_paths)} in {experiment_dir}"
        )
    if len(dir_paths) < AGG_NUM:
        raise ValueError(
            f"Need at least {AGG_NUM} runs for aggregation, but only found {len(dir_paths)} in {experiment_dir}"
        )

    jobs = []
    for folder in dir_paths:
        jobs.append(get_job(folder))

    random.seed(RANDOM_SEED)
    baseline_indices = random.sample(list(range(len(jobs))), NUM)
    agg_index_list = []
    for baseline_index in baseline_indices:
        agg_indices = random.sample(
            [i for i in range(len(jobs)) if i != baseline_index], AGG_NUM - 1
        )
        agg_indices.append(baseline_index)
        agg_index_list.append(agg_indices)

    rows = []
    for baseline_name, agg_func in [
        ("without", None),
        ("major", majority_scoring),
        ("borda", borda_scoring),
        ("range", range_scoring),
    ]:
        mean_hits, epsilon, ambiguity, discrepancy = evaluation(
            jobs, agg_index_list, K, agg_func=agg_func
        )
        rows.append(
            {
                "Model": MODEL,
                "Dataset": DATASET,
                "Baselines": baseline_name,
                "Hits": mean_hits,
                "Epsilon": epsilon,
                "Alpha": ambiguity,
                "Delta": discrepancy,
            }
        )

    df = pd.DataFrame(rows)
    output_dir = os.path.dirname(OUTPUT_CSV)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved results to: {OUTPUT_CSV}")


if __name__ == "__main__":
    run_experiment()
