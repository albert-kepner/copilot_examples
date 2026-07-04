"""
cluster_state.py

Defines ClusterState, which manages the global index dictionaries and cluster
registry used during record processing.

The Business enum is imported from cluster.py to avoid a circular import
(cluster_state imports Cluster; placing Business here would require cluster.py
to import from cluster_state.py).
"""

from __future__ import annotations

from cluster import Business, Cluster


class ClusterState:
    """Global bookkeeping state for the customer-record clustering algorithm.

    Maintains three identifier-to-cluster-id index dictionaries (one per
    identifier type) and a cluster-id-to-Cluster registry.  Records are
    submitted one at a time via add_record(); the state object handles all
    cluster creation and merging internally.

    Attributes:
        next_cluster_id:      Counter used to issue unique, ascending cluster IDs.
        npi_to_cluster:       Maps each known NPI value to its current cluster ID.
        ncpdp_to_cluster:     Maps each known NCPDP value to its current cluster ID.
        dea_to_cluster:       Maps each known DEA value to its current cluster ID.
        cluster_id_to_cluster: Maps cluster IDs to their Cluster objects.
    """

    def __init__(self) -> None:
        self.next_cluster_id: int = 1
        self.npi_to_cluster: dict[str, int] = {}
        self.ncpdp_to_cluster: dict[str, int] = {}
        self.dea_to_cluster: dict[str, int] = {}
        self.cluster_id_to_cluster: dict[int, Cluster] = {}

    def get_next_cluster_id(self) -> int:
        """Return the next unique cluster ID and advance the internal counter.

        Each call returns a value one greater than the previous call.  The
        first call returns 1.

        Returns:
            The next ascending integer cluster ID.
        """
        cluster_id = self.next_cluster_id
        self.next_cluster_id += 1
        return cluster_id

    def add_record(
        self,
        business: Business,
        record_ids: tuple[str | None, str | None, str | None],
    ) -> None:
        """Process one incoming business record, updating cluster state.

        record_ids is always ordered (npi, ncpdp, dea).  Any element may be
        None, but not all three simultaneously.

        Algorithm outline:
        1. Construct a new Cluster for this record and assign it a cluster ID.
        2. Collect all *existing* clusters whose identifier sets overlap with
           any non-None identifier in record_ids (up to 3 matches are possible).
        3. If no existing cluster matches, register the new cluster in all
           relevant index dicts and in cluster_id_to_cluster.
        4. If one or more existing clusters match, choose one as the survivor
           and call survivor.merge_from() for each of the remaining clusters
           (including the freshly created one).  Remove absorbed clusters from
           cluster_id_to_cluster and update all three identifier index dicts so
           that every moved identifier points to the survivor's cluster ID.

        Invariant: after each call, every unique identifier value present in
        the state maps to exactly one cluster.

        Args:
            business:   The McKesson business unit submitting this record.
            record_ids: A tuple of (npi, ncpdp, dea).
        """
        self._validate_record_ids(record_ids)

        matching_cluster_ids = self._get_matching_cluster_ids(record_ids)

        new_cluster = Cluster(business=business, record_ids=record_ids)
        new_cluster.cluster_id = self.get_next_cluster_id()

        if not matching_cluster_ids:
            self._register_cluster(new_cluster)
            return

        survivor_id = min(matching_cluster_ids)
        survivor = self.cluster_id_to_cluster[survivor_id]

        for cluster_id in sorted(matching_cluster_ids):
            if cluster_id == survivor_id:
                continue
            absorbed = self.cluster_id_to_cluster[cluster_id]
            survivor.merge_from(absorbed)
            self._repoint_indexes_for_cluster(absorbed, survivor_id)
            del self.cluster_id_to_cluster[cluster_id]

        survivor.merge_from(new_cluster)
        self._repoint_indexes_for_cluster(new_cluster, survivor_id)

    @staticmethod
    def _validate_record_ids(
        record_ids: tuple[str | None, str | None, str | None],
    ) -> None:
        if all(identifier is None for identifier in record_ids):
            raise ValueError("record_ids cannot be all None")

    def _get_matching_cluster_ids(
        self,
        record_ids: tuple[str | None, str | None, str | None],
    ) -> set[int]:
        npi, ncpdp, dea = record_ids
        matches: set[int] = set()

        if npi is not None and npi in self.npi_to_cluster:
            matches.add(self.npi_to_cluster[npi])
        if ncpdp is not None and ncpdp in self.ncpdp_to_cluster:
            matches.add(self.ncpdp_to_cluster[ncpdp])
        if dea is not None and dea in self.dea_to_cluster:
            matches.add(self.dea_to_cluster[dea])

        return matches

    def _register_cluster(self, cluster: Cluster) -> None:
        self.cluster_id_to_cluster[cluster.cluster_id] = cluster
        self._repoint_indexes_for_cluster(cluster, cluster.cluster_id)

    def _repoint_indexes_for_cluster(self, cluster: Cluster, cluster_id: int) -> None:
        for npi in cluster.npi_set:
            self.npi_to_cluster[npi] = cluster_id
        for ncpdp in cluster.ncpdp_set:
            self.ncpdp_to_cluster[ncpdp] = cluster_id
        for dea in cluster.dea_set:
            self.dea_to_cluster[dea] = cluster_id

