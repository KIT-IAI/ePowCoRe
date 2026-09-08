"""
Internal multiprocessing helpers for DeepDiff.

Phase 1 scope: parallelize the (added_hash x removed_hash) rough-distance loop
in ``DeepDiff._get_most_in_common_pairs_in_iterables`` for ``ignore_order=True``.

Determinism contract (see docs/multi_processing.md):
- Pair selection happens in the parent only.
- Workers compute distances. The parent submits jobs in a stable index order
  matching the serial nested loop and merges results by that index.
- Worker completion order (``as_completed``) never affects the public output.

Only module-level callables live here so the module is safe under the
``spawn`` start method (macOS/Windows).
"""

import os
import pickle
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, cast


DEFAULT_MAX_WORKERS = 4
DEFAULT_THRESHOLD = 64

# Keys we lift out of a worker's internal _stats and ship back to the parent.
# These mirror the same string constants used by ``deepdiff/diff.py``; we keep
# string literals here to avoid importing diff.py at module load (which would
# create an import cycle under spawn).
_WORKER_STATS_COUNTER_KEYS = ('DIFF COUNT', 'PASSES COUNT', 'DISTANCE CACHE HIT COUNT')
_WORKER_STATS_FLAG_KEYS = ('MAX PASS LIMIT REACHED', 'MAX DIFF LIMIT REACHED')


def _extract_worker_stats(diff_instance: Any) -> Dict[str, Any]:
    """Pull a small, picklable stats snapshot off a worker-local DeepDiff.

    Returns a dict with integer counters plus boolean limit flags. Missing keys
    are tolerated so this stays robust if ``_stats`` shrinks at the end of
    ``__init__`` (it currently deletes ``DISTANCE CACHE ENABLED`` and the
    ``PREVIOUS *`` bookkeeping keys before we get here).
    """
    stats = getattr(diff_instance, '_stats', None) or {}
    delta: Dict[str, Any] = {}
    for key in _WORKER_STATS_COUNTER_KEYS:
        delta[key] = int(stats.get(key, 0) or 0)
    for key in _WORKER_STATS_FLAG_KEYS:
        delta[key] = bool(stats.get(key, False))
    return delta


def _aggregate_worker_stats(deltas: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Sum counter keys and OR-merge limit flags across worker deltas."""
    out: Dict[str, Any] = {key: 0 for key in _WORKER_STATS_COUNTER_KEYS}
    for key in _WORKER_STATS_FLAG_KEYS:
        out[key] = False
    for delta in deltas:
        if not delta:
            continue
        for key in _WORKER_STATS_COUNTER_KEYS:
            out[key] += int(delta.get(key, 0) or 0)
        for key in _WORKER_STATS_FLAG_KEYS:
            if delta.get(key):
                out[key] = True
    return out


@dataclass(frozen=True)
class MPConfig:
    """Normalized internal multiprocessing configuration."""
    enabled: bool
    workers: int
    threshold: int

    def should_parallelize(self, n_jobs: int) -> bool:
        return self.enabled and self.workers > 1 and n_jobs >= self.threshold


def normalize_mp_config(
    multiprocessing: Any,
    multiprocessing_workers: Optional[int],
    multiprocessing_threshold: Optional[int],
) -> MPConfig:
    """Validate and normalize the public multiprocessing parameters.

    ``multiprocessing`` accepts True/False. ``multiprocessing_workers`` accepts
    None or a positive int. ``multiprocessing_threshold`` accepts None or a
    non-negative int.
    """
    if multiprocessing not in (True, False, 0, 1):
        raise ValueError(
            "multiprocessing must be True or False; got %r" % (multiprocessing,)
        )
    enabled = bool(multiprocessing)

    if multiprocessing_workers is None:
        cpu = os.cpu_count() or 1
        workers = min(DEFAULT_MAX_WORKERS, cpu)
    else:
        if not isinstance(multiprocessing_workers, int) or multiprocessing_workers < 1:
            raise ValueError(
                "multiprocessing_workers must be None or a positive integer; got %r"
                % (multiprocessing_workers,)
            )
        workers = multiprocessing_workers

    if multiprocessing_threshold is None:
        threshold = DEFAULT_THRESHOLD
    else:
        if not isinstance(multiprocessing_threshold, int) or multiprocessing_threshold < 0:
            raise ValueError(
                "multiprocessing_threshold must be None or a non-negative integer; got %r"
                % (multiprocessing_threshold,)
            )
        threshold = multiprocessing_threshold

    return MPConfig(enabled=enabled, workers=workers, threshold=threshold)


def is_pickleable(obj: Any) -> bool:
    """Return True if ``obj`` round-trips through ``pickle.dumps`` cleanly.

    Used to decide whether parallel execution is safe for a given input.
    A False result triggers serial fallback for that section.
    """
    try:
        pickle.dumps(obj)
        return True
    except Exception:
        return False


def _sanitize_parameters_for_worker(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Strip parent-process-only state from a ``_parameters`` snapshot.

    The parent's ``_parameters`` may carry references that should not be reused
    inside a worker (mutable shared caches) or that would cause nested
    multiprocessing inside the worker. This produces a copy safe to ship.
    """
    sanitized = dict(parameters)
    # Force serial inside the worker: a nested ProcessPoolExecutor would
    # deadlock or just waste process spawn time. Both the public flag and
    # the normalized config object must be neutralized — recursive DeepDiff
    # calls read ``_mp_config`` directly when ``_parameters`` is supplied.
    sanitized['multiprocessing'] = False
    sanitized['_mp_config'] = MPConfig(enabled=False, workers=1, threshold=0)
    sanitized.pop('_distance_cache', None)
    sanitized.pop('hashes', None)
    sanitized.pop('_numpy_paths', None)
    sanitized.pop('_stats', None)
    sanitized.pop('group_by_keys', None)
    sanitized.pop('tree', None)
    sanitized.pop('_iterable_opcodes', None)
    sanitized.pop('is_root', None)
    return sanitized


def _distance_worker(
    job: Tuple[int, Dict[str, Any], Any, Any, Any, Any],
) -> Tuple[int, float, Dict[str, Any]]:
    """Compute the rough distance between two items in a worker process.

    ``job`` layout matches what ``compute_distances_parallel`` ships:
    ``(job_index, sanitized_parameters, removed_item, added_item,
        original_type, iterable_compare_func)``.

    The worker constructs a fresh root ``DeepDiff`` (no shared parent state),
    requests the DELTA_VIEW so we hit the same code path as the serial call in
    ``_get_rough_distance_of_hashed_objs``, and returns the resulting float
    plus a ``_extract_worker_stats`` snapshot so the parent can aggregate
    diff/pass/cache-hit counts into its WORKER_* stats keys.
    """
    # Imported here to keep module import cheap and to dodge any circular
    # import surprises under spawn.
    from deepdiff.diff import DeepDiff
    from deepdiff.helper import DELTA_VIEW

    job_index, parameters, removed_item, added_item, original_type, iterable_compare_func = job
    diff = DeepDiff(
        removed_item,
        added_item,
        _parameters=parameters,
        view=DELTA_VIEW,
        _original_type=original_type,
        iterable_compare_func=iterable_compare_func,
        # The worker is spawned without _shared_parameters, so DeepDiff treats
        # it as a root run and would purge ``_distance_cache``/``hashes`` at
        # the end of __init__. We need them alive for the _get_rough_distance
        # call below, hence cache_purge_level=0.
        cache_purge_level=0,
    )
    return job_index, cast(float, diff._get_rough_distance()), _extract_worker_stats(diff)


def compute_distances_parallel(
    jobs: List[Tuple[Any, Any, Any, Any]],
    parameters: Dict[str, Any],
    original_type: Any,
    iterable_compare_func: Optional[Callable],
    config: MPConfig,
) -> Optional[Tuple[Dict[Tuple[Any, Any], float], Dict[str, Any]]]:
    """Run ``_distance_worker`` over ``jobs`` and return distances by pair.

    ``jobs`` is a list of ``(added_hash, removed_hash, added_item, removed_item)``
    tuples in the exact order the serial nested loop visits them. The parent
    is responsible for that ordering; this helper does not reorder anything.

    Returns:
        ``(distances_by_pair, aggregated_worker_stats)`` where the first item
        is a dict ``{(added_hash, removed_hash): distance}`` and the second is
        the aggregated ``_extract_worker_stats`` snapshot summed across all
        workers (counter keys summed, limit flags OR-merged). Returns
        ``None`` if the section is unsafe to parallelize (unpickleable
        inputs/parameters, worker import error, etc.). On ``None`` the caller
        MUST fall back to the serial path so correctness is preserved.

    Workers may finish out of order; we collect results into a dict keyed by
    the original job index, so callers see the same result regardless of
    completion order.
    """
    if not jobs:
        return {}, _aggregate_worker_stats([])

    sanitized_params = _sanitize_parameters_for_worker(parameters)

    # Picklability check. Failing fast here means a clear serial fallback
    # rather than an opaque worker crash.
    if not is_pickleable(sanitized_params):
        return None
    if iterable_compare_func is not None and not is_pickleable(iterable_compare_func):
        return None
    # Sample-pickle items: full check of every job is expensive, but pickling
    # the first job catches the common "lambda in custom_operators" failure
    # while keeping overhead bounded.
    if not is_pickleable(jobs[0]):
        return None

    # Imported lazily so importing this module does not pay the cost when
    # multiprocessing is disabled.
    from concurrent.futures import ProcessPoolExecutor, as_completed

    payloads = []
    for i, job in enumerate(jobs):
        added_item = job[2]
        removed_item = job[3]
        payloads.append(
            (i, sanitized_params, removed_item, added_item, original_type, iterable_compare_func)
        )

    results_by_index: Dict[int, float] = {}
    stats_deltas: List[Dict[str, Any]] = []
    try:
        with ProcessPoolExecutor(max_workers=config.workers) as executor:
            futures = [executor.submit(_distance_worker, payload) for payload in payloads]
            for future in as_completed(futures):
                # Re-raise worker exceptions in the parent so they surface as
                # normal DeepDiff exceptions instead of being swallowed.
                idx, distance, stats_delta = future.result()
                results_by_index[idx] = distance
                stats_deltas.append(stats_delta)
    except (pickle.PicklingError, AttributeError, TypeError):
        # Pickling/spawn-related failures: surface as a serial fallback rather
        # than crashing the diff. Other exceptions (worker logic bugs, user
        # callback errors) propagate.
        return None

    out: Dict[Tuple[Any, Any], float] = {}
    for i, job in enumerate(jobs):
        out[(job[0], job[1])] = results_by_index[i]
    return out, _aggregate_worker_stats(stats_deltas)


def _hash_worker(job: Tuple[int, Any, str, Dict[str, Any]]) -> Tuple[int, Optional[str]]:
    """Hash a single iterable item in a worker process.

    ``job`` layout: ``(job_index, item, parent_path, deephash_parameters)``.
    The worker constructs a fresh ``DeepHash`` (no shared parent state) and
    looks up the resulting top-level hash for ``item``. Returns
    ``(job_index, item_hash)`` where ``item_hash`` is None if the item could
    not be processed — the parent treats that exactly like the serial path's
    ``KeyError`` / ``unprocessed`` skip.

    UnicodeDecodeError and NotImplementedError propagate as in the serial
    path; other exceptions surface in the parent through ``future.result()``.
    """
    # Imported here to dodge spawn/import-cycle surprises.
    from deepdiff.deephash import DeepHash
    from deepdiff.helper import unprocessed

    job_index, item, parent_path, parameters = job
    deep_hash = DeepHash(
        item,
        hashes=None,
        parent=parent_path,
        apply_hash=True,
        **parameters,
    )
    try:
        item_hash = deep_hash[item]
    except KeyError:
        return job_index, None
    if item_hash is unprocessed:
        return job_index, None
    return job_index, item_hash


def _subtree_diff_worker(
    job: Tuple[int, Dict[str, Any], Any, Any, Any],
) -> Tuple[int, List[Tuple[str, Any]], Dict[str, Any]]:
    """Run one paired-item subtree diff in a worker process.

    ``job`` layout: ``(job_index, sanitized_parameters, t1, t2, _original_type)``.
    The worker constructs a fresh root ``DeepDiff`` (no shared parent state),
    requests the TREE_VIEW so ``self.tree`` is populated and walks it once to
    flatten the leaves into ``[(report_type, leaf_difflevel), ...]``.

    The parent rebases each leaf's up-chain onto its own ``change_level`` so
    paths come out as if the diff had run inline. Returning bare DiffLevel
    objects is acceptable here because we already proved they pickle and
    re-attach cleanly (see tests/test_multiprocessing.py).
    """
    # Imported here to keep module import cheap and to dodge any circular
    # import surprises under spawn.
    from deepdiff.diff import DeepDiff
    from deepdiff.helper import TREE_VIEW

    job_index, parameters, t1, t2, _original_type = job
    diff = DeepDiff(
        t1, t2,
        _parameters=parameters,
        view=TREE_VIEW,
        _original_type=_original_type,
        # Keep cache+tree alive past __init__ so the post-walk below sees the
        # populated tree (cache_purge_level mirrors what _distance_worker uses).
        cache_purge_level=0,
    )
    entries: List[Tuple[str, Any]] = []
    for report_type, levels in diff.tree.items():
        if report_type == 'deep_distance':
            continue
        for leaf in levels:
            entries.append((report_type, leaf))
    return job_index, entries, _extract_worker_stats(diff)


def compute_subtree_diffs_parallel(
    jobs: List[Tuple[Any, Any]],
    parameters: Dict[str, Any],
    original_type: Any,
    config: MPConfig,
) -> Optional[Tuple[List[List[Tuple[str, Any]]], Dict[str, Any]]]:
    """Run ``_subtree_diff_worker`` over ``jobs`` and return per-job entries.

    ``jobs`` is a list of ``(t1_item, t2_item)`` tuples in the exact order
    the serial paired-iteration code visits them. Returns
    ``(entries_by_job, aggregated_worker_stats)`` where ``entries_by_job`` is
    a list aligned to job order — each element is ``[(report_type,
    leaf_difflevel), ...]`` suitable for the parent to rebase and merge into
    its tree — and ``aggregated_worker_stats`` is the per-batch ``_stats``
    deltas summed across workers (counters summed, limit flags OR-merged).
    Returns ``None`` when the section is unsafe to parallelize (unpickleable
    parameters/items, worker import error). On ``None`` the caller MUST run
    the same jobs serially so correctness is preserved.

    Workers may finish out of order; results are collected by their original
    job index so the merge order is identical regardless of completion order.
    """
    if not jobs:
        return [], _aggregate_worker_stats([])

    sanitized_params = _sanitize_parameters_for_worker(parameters)

    if not is_pickleable(sanitized_params):
        return None
    # Sample-pickle the first job; cheap shield against the common
    # "lambda in custom_operators" / unpickleable item failure.
    if not is_pickleable(jobs[0]):
        return None

    from concurrent.futures import ProcessPoolExecutor, as_completed

    payloads = [
        (i, sanitized_params, t1_item, t2_item, original_type)
        for i, (t1_item, t2_item) in enumerate(jobs)
    ]

    results_by_index: Dict[int, List[Tuple[str, Any]]] = {}
    stats_deltas: List[Dict[str, Any]] = []
    try:
        with ProcessPoolExecutor(max_workers=config.workers) as executor:
            futures = [executor.submit(_subtree_diff_worker, payload) for payload in payloads]
            for future in as_completed(futures):
                idx, entries, stats_delta = future.result()
                results_by_index[idx] = entries
                stats_deltas.append(stats_delta)
    except (pickle.PicklingError, AttributeError, TypeError):
        return None

    return (
        [results_by_index[i] for i in range(len(jobs))],
        _aggregate_worker_stats(stats_deltas),
    )


def compute_hashes_parallel(
    jobs: List[Tuple[Any, str]],
    deephash_parameters: Dict[str, Any],
    config: MPConfig,
) -> Optional[List[Optional[str]]]:
    """Run ``_hash_worker`` over ``jobs`` and return per-item hashes.

    ``jobs`` is a list of ``(item, parent_path)`` tuples in the exact order
    the serial enumerate-loop visits them. Returns a list aligned to that
    order, with ``None`` for items the worker could not hash. Returns
    ``None`` when the section is unsafe to parallelize (unpickleable
    parameters/items, worker import error). On ``None`` the caller MUST fall
    back to the serial path.

    Workers may finish out of order; results are collected by their original
    index so callers see the same output regardless of completion order.
    Note: child object hashes computed inside each worker are NOT merged
    back into the parent's ``self.hashes`` — id-based keys for unhashable
    sub-objects would not match across process boundaries. Parent code that
    relies on the iterable-level hash being present must continue to compute
    it serially after the per-item parallel pass.
    """
    if not jobs:
        return []

    if not is_pickleable(deephash_parameters):
        return None
    # Sample-pickle the first job; cheap shield against the common
    # "lambda in custom_operators" or unpickleable item failure.
    if not is_pickleable(jobs[0]):
        return None

    from concurrent.futures import ProcessPoolExecutor, as_completed

    payloads = [
        (i, item, parent_path, deephash_parameters)
        for i, (item, parent_path) in enumerate(jobs)
    ]

    results_by_index: Dict[int, Optional[str]] = {}
    try:
        with ProcessPoolExecutor(max_workers=config.workers) as executor:
            futures = [executor.submit(_hash_worker, payload) for payload in payloads]
            for future in as_completed(futures):
                idx, item_hash = future.result()
                results_by_index[idx] = item_hash
    except (pickle.PicklingError, AttributeError, TypeError):
        return None

    return [results_by_index[i] for i in range(len(jobs))]
