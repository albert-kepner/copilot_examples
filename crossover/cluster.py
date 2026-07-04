"""
cluster.py

Defines the Business enum and Cluster class.

Note on module structure: The Business enum is defined here (rather than in
cluster_state.py as originally specified) to avoid a circular import.
cluster_state.py imports both Business and Cluster from this module.
"""

from __future__ import annotations

from enum import Enum


class Business(Enum):
    """McKesson business units that contribute customer records."""

    SL = "SL"
    MH = "MH"
    ERX = "ERx"   # Enum name is ERX; string value matches example dicts ("ERx")
    PSAS = "PSAS"


class Cluster:
    """Represents a single customer cluster.

    A cluster begins as a single business record and may grow by merging with
    other clusters that share one or more identifier values.

    Attributes:
        cluster_id: Unique integer ID assigned by ClusterState.
        customer_record_counts: Number of source records from each business
            that have been merged into this cluster.  Keys are business
            abbreviation strings (e.g. "SL", "ERx").
        npi_set:   All NPI identifier values belonging to this cluster.
        ncpdp_set: All NCPDP identifier values belonging to this cluster.
        dea_set:   All DEA identifier values belonging to this cluster.
    """

    def __init__(
        self,
        business: Business,
        record_ids: tuple[str | None, str | None, str | None],
    ) -> None:
        """Initialize a new cluster from a single business record.

        The cluster_id is set to 0 here as a placeholder; ClusterState is
        responsible for assigning the real ID via get_next_cluster_id().

        Args:
            business:   The McKesson business unit this record belongs to.
            record_ids: A tuple of (npi, ncpdp, dea).  Any element may be
                        None, but not all three simultaneously.
        """
        self.cluster_id: int = 0  # assigned by ClusterState after construction
        self.customer_record_counts: dict[str, int] = {b.value: 0 for b in Business}
        self.npi_set: set[str] = set()
        self.ncpdp_set: set[str] = set()
        self.dea_set: set[str] = set()
        pass  # TODO: implement

    def merge_from(self, other: Cluster) -> None:
        """Absorb another cluster into this one (pairwise merge).

        All identifier sets and record counts from *other* are incorporated
        into *self*.  After this call the caller (ClusterState.add_record) is
        responsible for removing *other* from the cluster registry and updating
        all identifier-to-cluster index dictionaries.

        Args:
            other: The cluster to be absorbed.  It should not be used after
                   this call.
        """
        pass  # TODO: implement

