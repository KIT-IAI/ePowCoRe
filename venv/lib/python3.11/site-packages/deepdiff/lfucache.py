from collections import defaultdict
from cachebox import LRUCache
from deepdiff.helper import SetOrdered, not_found


class DistanceCache:
    """
    Native bounded cache used by DeepDiff's distance calculations.

    DeepDiff historically used a pure Python LFU cache here. The distance-cache
    hot path benefits more from cachebox's native mapping operations than from
    preserving LFU eviction semantics.
    """

    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError('Capacity of DistanceCache needs to be positive.')  # pragma: no cover.
        self.cache = LRUCache(capacity)

    def get(self, key):
        return self.cache.get(key, not_found)

    def set(self, key, report_type=None, value=None):
        if report_type:
            content = self.cache.get(key, None)
            if content is None:
                content = defaultdict(SetOrdered)
            content[report_type].add(value)
            value = content
        self.cache.insert(key, value)

    def __contains__(self, key):
        return key in self.cache


LFUCache = DistanceCache


class DummyLFU:

    def __init__(self, *args, **kwargs):
        pass

    set = __init__

    def get(self, *args, **kwargs):
        return not_found

    def __contains__(self, key):
        return False
