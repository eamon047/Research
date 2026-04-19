import argparse
import os
import random
from collections import defaultdict
from dataclasses import dataclass

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


@dataclass(frozen=True)
class LocalExperimentConfig:
    experiments_root: str = "LibKGE/local"
    model: str = "RotatE"
    dataset: str = "FB15k237"
    experiment_name: str = "RotatE_FB15k237"
    num: int = 7
    agg_num: int = 7
    k: int = 10
    random_seed: int = 0
    output_csv: str = "results/RotatE_FB15k237_num7_agg7_k10.csv"


def default_local_experiment_config(output_csv=None):
    config = LocalExperimentConfig()
    if output_csv is None:
        return config
    return LocalExperimentConfig(
        experiments_root=config.experiments_root,
        model=config.model,
        dataset=config.dataset,
        experiment_name=config.experiment_name,
        num=config.num,
        agg_num=config.agg_num,
        k=config.k,
        random_seed=config.random_seed,
        output_csv=output_csv,
    )


def argparse_bool_type(v):
    "Type for argparse that correctly treats Boolean values"
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    if v.lower() in ("no", "false", "f", "n", "0"):
        return False
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

    # Analysis scripts often run on login nodes without visible GPUs. In that
    # case, force CPU instead of trying to restore checkpoints onto cuda.
    job_device = config.get("job.device")
    if isinstance(job_device, str) and job_device.startswith("cuda") and not torch.cuda.is_available():
        config.set("job.device", "cpu")

    # Reduce GPU memory pressure during multiplicity evaluation.
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


def resolve_run_directories(experiment_dir):
    if not os.path.isdir(experiment_dir):
        raise FileNotFoundError(f"Experiment directory does not exist: {experiment_dir}")

    return [
        os.path.join(experiment_dir, name)
        for name in sorted(os.listdir(experiment_dir))
        if os.path.isdir(os.path.join(experiment_dir, name))
        and os.path.isfile(os.path.join(experiment_dir, name, "config.yaml"))
    ]


def load_jobs_from_experiment(experiment_dir, num_required, agg_num_required):
    dir_paths = resolve_run_directories(experiment_dir)

    if len(dir_paths) < num_required:
        raise ValueError(
            f"Need at least {num_required} runs, but only found {len(dir_paths)} in {experiment_dir}"
        )
    if len(dir_paths) < agg_num_required:
        raise ValueError(
            f"Need at least {agg_num_required} runs for aggregation, but only found {len(dir_paths)} in {experiment_dir}"
        )

    jobs = []
    for folder in dir_paths:
        jobs.append(get_job(folder))
    return jobs


def sample_aggregation_indices(num_jobs, num, agg_num, random_seed):
    random.seed(random_seed)
    baseline_indices = random.sample(list(range(num_jobs)), num)
    agg_index_list = []
    for baseline_index in baseline_indices:
        agg_indices = random.sample(
            [i for i in range(num_jobs) if i != baseline_index], agg_num - 1
        )
        agg_indices.append(baseline_index)
        agg_index_list.append(agg_indices)
    return agg_index_list


def majority_scoring(scores):
    max_indices = torch.argmax(scores, dim=1)
    return F.one_hot(max_indices, num_classes=scores.shape[1])


def borda_scoring(scores):
    _, indices = torch.sort(scores, descending=True, dim=1)
    borda_scores = torch.arange(
        scores.shape[1] - 1, -1, -1, device=scores.device
    ).expand_as(scores)
    return torch.zeros_like(scores, dtype=borda_scores.dtype).scatter_(
        1, indices, borda_scores
    )


def range_scoring(scores):
    min_score = torch.min(scores)
    max_score = torch.max(scores)
    if torch.equal(min_score, max_score):
        return torch.zeros_like(scores)
    return 2 * (scores - min_score) / (max_score - min_score) - 1


def compute_rank_data(jobs, agg_func=None, include_relations=False):
    num_entities = jobs[0].dataset.num_entities()
    device = jobs[0].device
    loader = jobs[0].loader
    labels_for_ranking = defaultdict(lambda: None)
    s_ranks = []
    o_ranks = []
    relations = []

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
        if include_relations:
            relations.append(p)

    rank_data = {
        "s_ranks": torch.cat(s_ranks),
        "o_ranks": torch.cat(o_ranks),
    }
    if include_relations:
        rank_data["relations"] = torch.cat(relations)
    return rank_data


def compute_rank_outputs(jobs, agg_index_list, agg_func=None, include_relations=False):
    rank_outputs = []
    query_relations = None

    for agg_indices in agg_index_list:
        agg_jobs = [jobs[i] for i in agg_indices]
        rank_data = compute_rank_data(
            agg_jobs, agg_func=agg_func, include_relations=include_relations
        )
        rank_outputs.append(torch.cat([rank_data["s_ranks"], rank_data["o_ranks"]]))
        if include_relations and query_relations is None:
            relations = rank_data["relations"]
            query_relations = torch.cat([relations, relations])

    return rank_outputs, query_relations


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


def build_eligible_mask(rank_outputs, k):
    return torch.any(torch.stack(rank_outputs) < k, dim=0)


def evaluate_rank_outputs(rank_outputs, k):
    hits = [hits_at_k(rank, k) for rank in rank_outputs]
    eligible_mask = build_eligible_mask(rank_outputs, k)
    eligible_support = int(torch.sum(eligible_mask).item())
    if eligible_support == 0:
        ambiguity = float("nan")
        discrepancy = float("nan")
    else:
        masked_ranks = [rank[eligible_mask] for rank in rank_outputs]
        ambiguity = ambiguity_at_k(masked_ranks, k)
        discrepancy = discrepancy_at_k(masked_ranks, k)

    return {
        "mean_hits": sum(hits) / len(hits),
        "epsilon": max(hits) - min(hits),
        "ambiguity": ambiguity,
        "discrepancy": discrepancy,
        "eligible_support": eligible_support,
    }


def default_output_name(config):
    return f"results/{config.experiment_name}_num{config.num}_agg{config.agg_num}_k{config.k}.csv"


def parse_local_experiment_args(description, default_output_csv=None):
    defaults = default_local_experiment_config(
        output_csv=default_output_csv or default_local_experiment_config().output_csv
    )
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--experiments-root", default=defaults.experiments_root)
    parser.add_argument("--model", default=defaults.model)
    parser.add_argument("--dataset", default=defaults.dataset)
    parser.add_argument("--experiment-name", default=defaults.experiment_name)
    parser.add_argument("--num", type=int, default=defaults.num)
    parser.add_argument("--agg-num", type=int, default=defaults.agg_num)
    parser.add_argument("--k", type=int, default=defaults.k)
    parser.add_argument("--seed", type=int, default=defaults.random_seed)
    parser.add_argument("--output-csv", default=defaults.output_csv)
    return parser.parse_args()
