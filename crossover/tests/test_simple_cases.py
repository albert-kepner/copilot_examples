from __future__ import annotations

from cluster import Business
from cluster_state import ClusterState


RecordIds = tuple[str | None, str | None, str | None]
InputRecord = tuple[Business, RecordIds]


def _apply_records(state: ClusterState, records: list[InputRecord]) -> None:
    for business, record_ids in records:
        state.add_record(business, record_ids)


def _cluster_snapshot(state: ClusterState) -> list[dict[str, object]]:
    snapshots: list[dict[str, object]] = []
    for cluster_id in sorted(state.cluster_id_to_cluster):
        cluster = state.cluster_id_to_cluster[cluster_id]
        snapshots.append(
            {
                "cluster_id": cluster_id,
                "npi": sorted(cluster.npi_set),
                "ncpdp": sorted(cluster.ncpdp_set),
                "dea": sorted(cluster.dea_set),
                "customer_record_counts": dict(cluster.customer_record_counts),
            }
        )
    return snapshots


def _print_case(title: str, intended_outcome: str, records: list[InputRecord], state: ClusterState) -> None:
    print(f"\n=== {title} ===")
    print(f"Intended outcome: {intended_outcome}")
    print("Input records:")
    for idx, (business, record_ids) in enumerate(records, start=1):
        npi, ncpdp, dea = record_ids
        print(f"  {idx}. business={business.value}, npi={npi}, ncpdp={ncpdp}, dea={dea}")

    print("Resulting clusters:")
    for snapshot in _cluster_snapshot(state):
        print(f"  Cluster {snapshot['cluster_id']}:")
        print(f"    npi={snapshot['npi']}")
        print(f"    ncpdp={snapshot['ncpdp']}")
        print(f"    dea={snapshot['dea']}")
        print(f"    customer_record_counts={snapshot['customer_record_counts']}")


def test_single_record_creates_one_cluster() -> None:
    state = ClusterState()
    records: list[InputRecord] = [
        (Business.SL, ("npi1", "ncpdp1", "dea1")),
    ]

    _apply_records(state, records)
    _print_case(
        "Case 1 - single record",
        "One cluster with one record count in SL and one value in each identifier set.",
        records,
        state,
    )

    snapshots = _cluster_snapshot(state)
    assert len(snapshots) == 1
    assert snapshots[0]["npi"] == ["npi1"]
    assert snapshots[0]["ncpdp"] == ["ncpdp1"]
    assert snapshots[0]["dea"] == ["dea1"]
    assert snapshots[0]["customer_record_counts"] == {"SL": 1, "MH": 0, "ERx": 0, "PSAS": 0}


def test_two_independent_records_same_business_stay_separate() -> None:
    state = ClusterState()
    records: list[InputRecord] = [
        (Business.SL, ("npi1", "ncpdp1", None)),
        (Business.SL, ("npi2", "ncpdp2", None)),
    ]

    _apply_records(state, records)
    _print_case(
        "Case 2 - independent records",
        "Two separate clusters because no identifier overlaps.",
        records,
        state,
    )

    snapshots = _cluster_snapshot(state)
    assert len(snapshots) == 2
    assert sorted(snapshot["npi"] for snapshot in snapshots) == [["npi1"], ["npi2"]]


def test_shared_npi_merges_within_single_business() -> None:
    state = ClusterState()
    records: list[InputRecord] = [
        (Business.SL, ("npi1", "ncpdp1", None)),
        (Business.SL, ("npi1", "ncpdp2", "dea2")),
    ]

    _apply_records(state, records)
    _print_case(
        "Case 3 - shared npi",
        "One merged cluster with SL count=2 and union of identifiers.",
        records,
        state,
    )

    snapshots = _cluster_snapshot(state)
    assert len(snapshots) == 1
    assert snapshots[0]["npi"] == ["npi1"]
    assert snapshots[0]["ncpdp"] == ["ncpdp1", "ncpdp2"]
    assert snapshots[0]["dea"] == ["dea2"]
    assert snapshots[0]["customer_record_counts"] == {"SL": 2, "MH": 0, "ERx": 0, "PSAS": 0}


def test_shared_ncpdp_merges_across_two_businesses() -> None:
    state = ClusterState()
    records: list[InputRecord] = [
        (Business.SL, ("npi1", "ncpdp1", None)),
        (Business.MH, ("npi2", "ncpdp1", "dea2")),
    ]

    _apply_records(state, records)
    _print_case(
        "Case 4 - shared ncpdp across businesses",
        "One merged cluster with counts SL=1 and MH=1.",
        records,
        state,
    )

    snapshots = _cluster_snapshot(state)
    assert len(snapshots) == 1
    assert snapshots[0]["npi"] == ["npi1", "npi2"]
    assert snapshots[0]["ncpdp"] == ["ncpdp1"]
    assert snapshots[0]["dea"] == ["dea2"]
    assert snapshots[0]["customer_record_counts"] == {"SL": 1, "MH": 1, "ERx": 0, "PSAS": 0}


def test_bridge_record_merges_two_existing_clusters() -> None:
    state = ClusterState()
    records: list[InputRecord] = [
        (Business.SL, ("npi1", "ncpdp1", None)),
        (Business.MH, ("npi2", "ncpdp2", "dea2")),
        (Business.SL, (None, "ncpdp1", "dea2")),
    ]

    _apply_records(state, records)
    _print_case(
        "Case 5 - bridge merges clusters",
        "Third record bridges two clusters via ncpdp1 and dea2, resulting in one cluster.",
        records,
        state,
    )

    snapshots = _cluster_snapshot(state)
    assert len(snapshots) == 1
    assert snapshots[0]["npi"] == ["npi1", "npi2"]
    assert snapshots[0]["ncpdp"] == ["ncpdp1", "ncpdp2"]
    assert snapshots[0]["dea"] == ["dea2"]
    assert snapshots[0]["customer_record_counts"] == {"SL": 2, "MH": 1, "ERx": 0, "PSAS": 0}


def test_merges_can_chain_over_multiple_records() -> None:
    state = ClusterState()
    records: list[InputRecord] = [
        (Business.SL, ("npi1", "ncpdp1", None)),
        (Business.MH, (None, "ncpdp2", "dea2")),
        (Business.MH, ("npi3", "ncpdp2", None)),
        (Business.SL, ("npi1", None, "dea2")),
    ]

    _apply_records(state, records)
    _print_case(
        "Case 6 - chained merge",
        "Fourth record links earlier clusters by npi1 and dea2; all records end in one cluster.",
        records,
        state,
    )

    snapshots = _cluster_snapshot(state)
    assert len(snapshots) == 1
    assert snapshots[0]["npi"] == ["npi1", "npi3"]
    assert snapshots[0]["ncpdp"] == ["ncpdp1", "ncpdp2"]
    assert snapshots[0]["dea"] == ["dea2"]
    assert snapshots[0]["customer_record_counts"] == {"SL": 2, "MH": 2, "ERx": 0, "PSAS": 0}


def test_none_values_supported_when_not_all_none() -> None:
    state = ClusterState()
    records: list[InputRecord] = [
        (Business.SL, (None, "ncpdp1", None)),
        (Business.MH, (None, "ncpdp1", "dea1")),
    ]

    _apply_records(state, records)
    _print_case(
        "Case 7 - partial identifiers",
        "One cluster, empty npi set, with ncpdp1 and dea1 retained.",
        records,
        state,
    )

    snapshots = _cluster_snapshot(state)
    assert len(snapshots) == 1
    assert snapshots[0]["npi"] == []
    assert snapshots[0]["ncpdp"] == ["ncpdp1"]
    assert snapshots[0]["dea"] == ["dea1"]
    assert snapshots[0]["customer_record_counts"] == {"SL": 1, "MH": 1, "ERx": 0, "PSAS": 0}


def test_duplicate_record_values_increment_counts_not_sets() -> None:
    state = ClusterState()
    records: list[InputRecord] = [
        (Business.SL, ("npi1", "ncpdp1", "dea1")),
        (Business.SL, ("npi1", "ncpdp1", "dea1")),
    ]

    _apply_records(state, records)
    _print_case(
        "Case 8 - duplicate record values",
        "One cluster with singleton identifier sets and SL count incremented to 2.",
        records,
        state,
    )

    snapshots = _cluster_snapshot(state)
    assert len(snapshots) == 1
    assert snapshots[0]["npi"] == ["npi1"]
    assert snapshots[0]["ncpdp"] == ["ncpdp1"]
    assert snapshots[0]["dea"] == ["dea1"]
    assert snapshots[0]["customer_record_counts"] == {"SL": 2, "MH": 0, "ERx": 0, "PSAS": 0}

