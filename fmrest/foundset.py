"""Foundset class for collections of Records"""

import itertools
from .utils import cache_generator

class Foundset(object):
    """A set of Record instances

    Foundsets are used for both find results and portal data (related records)
    """
    def __init__(self, records):
        """Initialize the Foundset class.

        The foundset is cached while being consumed, so that subsequent iterations are possible.

        Parameters
        ----------
        records : generator
            Generator of Record instances representing the records in a foundset or
            related records from a portal.
        """
        self._records = records
        self._consumed = False

        # We hold the list of cached values and the state of completion in a list
        # idea: https://codereview.stackexchange.com/a/178780/151724
        self._cache = [[], False]

        # cache_generator will yield the values and handle the caching
        self._iter = cache_generator(self._records, self._cache)

    def __iter__(self):
        """Make foundset iterable.

        Returns iter for list of records already consumed from generator, or a chained object
        of cache list plus still-to-consume records. This makes sure foundsets can be properly used
        as a list.
        """

        if self._cache[1]:
            # all values have been cached
            return iter(self._cache[0])

        return itertools.chain(self._cache[0], self._iter)

    def __getitem__(self, index):
        """Return item at index in the iterator. If it's already cached, then return cached version.
        Otherwise consume until found.

        Parameters
        ----------
        index : int
        """
        while index >= len(self._cache[0]):
            try:
                next(self._iter)
            except StopIteration:
                break

        return self._cache[0][index]

    def __repr__(self):
        return '<Foundset consumed_records={} is_complete={}>'.format(
            len(self._cache[0]), self.is_complete
        )

    @property
    def is_complete(self):
        """Returns True if all values have been consumed. Otherwise False."""
        return self._cache[1]



    def to_df(self):
        """Returns a Pandas DataFrame of the Foundset. Must have Pandas installed.

        Note that portal data is not returned as part of the DataFrame.
        """
        try:
            import pandas as pd
        except ImportError as ex:
            raise Exception(
                "You need to have Pandas installed to use this feature. "
                "You can install it like this: 'pip install pandas'"
            ) from ex

        return pd.DataFrame(
            [r.to_dict(ignore_portals=True) for r in self]
        )
