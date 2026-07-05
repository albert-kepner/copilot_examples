from __future__ import annotations

import pytest

from cluster import Business
from cluster_state import ClusterState


RecordIds = tuple[str | None, str | None, str | None]
InputRecord = tuple[Business, RecordIds]


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


def _run_case(title: str, intended_outcome: str, records: list[InputRecord]) -> ClusterState:
    state = ClusterState()
    for business, record_ids in records:
        state.add_record(business, record_ids)
    _print_case(title, intended_outcome, records, state)
    return state


def test_all_none_identifiers_raise_value_error() -> None:
    state = ClusterState()
    records: list[InputRecord] = [(Business.SL, (None, None, None))]

    print("\n=== Case C1 - reject all-none record ===")
    print("Intended outcome: add_record raises ValueError and state remains empty.")
    print("Input records:")
    print("  1. business=SL, npi=None, ncpdp=None, dea=None")

    with pytest.raises(ValueError, match="record_ids cannot be all None"):
        state.add_record(*records[0])

    print("Resulting clusters:")
    print("  (none)")
    assert len(state.cluster_id_to_cluster) == 0


def test_bridge_record_merges_three_existing_clusters_in_one_step() -> None:
    records: list[InputRecord] = [
        (Business.SL, ("npi1", "ncpdp1", None)),
        (Business.MH, ("npi2", "ncpdp2", None)),
        (Business.SL, (None, "ncpdp3", "dea3")),
        (Business.MH, ("npi1", "ncpdp2", "dea3")),
    ]
    state = _run_case(
        "Case C2 - one record merges three clusters",
        "Fourth record should connect three existing clusters into one cluster.",
        records,
    )

    snapshots = _cluster_snapshot(state)
    assert len(snapshots) == 1
    assert snapshots[0]["npi"] == ["npi1", "npi2"]
    assert snapshots[0]["ncpdp"] == ["ncpdp1", "ncpdp2", "ncpdp3"]
    assert snapshots[0]["dea"] == ["dea3"]
    assert snapshots[0]["customer_record_counts"] == {"SL": 2, "MH": 2, "ERx": 0, "PSAS": 0}


def test_survivor_is_lowest_cluster_id_among_matching_clusters() -> None:
    records: list[InputRecord] = [
        (Business.SL, ("npi1", "ncpdp1", None)),
        (Business.MH, ("npi2", "ncpdp2", None)),
        (Business.SL, ("npi3", "ncpdp3", "dea3")),
        (Business.MH, ("npi2", None, "dea3")),
    ]
    state = _run_case(
        "Case C3 - survivor selection",
        "Fourth record matches cluster 2 and 3; cluster 2 should survive as lower matching ID.",
        records,
    )

    cluster_ids = sorted(state.cluster_id_to_cluster)
    assert cluster_ids == [1, 2]
    merged_snapshot = _cluster_snapshot(state)[1]
    assert merged_snapshot["cluster_id"] == 2
    assert merged_snapshot["npi"] == ["npi2", "npi3"]
    assert merged_snapshot["ncpdp"] == ["ncpdp2", "ncpdp3"]
    assert merged_snapshot["dea"] == ["dea3"]
    assert merged_snapshot["customer_record_counts"] == {"SL": 1, "MH": 2, "ERx": 0, "PSAS": 0}


def test_indexes_repoint_to_survivor_after_merge() -> None:
    records: list[InputRecord] = [
        (Business.SL, ("npi1", "ncpdp1", None)),
        (Business.MH, ("npi2", "ncpdp2", "dea2")),
        (Business.SL, ("npi1", None, "dea2")),
    ]
    state = _run_case(
        "Case C4 - index repoint",
        "After bridging merge, all ids should map to the survivor cluster id=1.",
        records,
    )

    assert sorted(state.cluster_id_to_cluster) == [1]
    assert state.npi_to_cluster["npi1"] == 1
    assert state.npi_to_cluster["npi2"] == 1
    assert state.ncpdp_to_cluster["ncpdp1"] == 1
    assert state.ncpdp_to_cluster["ncpdp2"] == 1
    assert state.dea_to_cluster["dea2"] == 1


def test_transitive_merge_chain_with_five_records() -> None:
    records: list[InputRecord] = [
        (Business.SL, ("npi1", "ncpdp1", None)),
        (Business.MH, ("npi2", "ncpdp2", None)),
        (Business.SL, (None, "ncpdp1", "dea1")),
        (Business.MH, ("npi3", None, "dea1")),
        (Business.SL, ("npi3", "ncpdp2", None)),
    ]
    state = _run_case(
        "Case C5 - transitive chain",
        "Five records should collapse into one cluster through transitive links across id types.",
        records,
    )

    snapshots = _cluster_snapshot(state)
    assert len(snapshots) == 1
    assert snapshots[0]["npi"] == ["npi1", "npi2", "npi3"]
    assert snapshots[0]["ncpdp"] == ["ncpdp1", "ncpdp2"]
    assert snapshots[0]["dea"] == ["dea1"]
    assert snapshots[0]["customer_record_counts"] == {"SL": 3, "MH": 2, "ERx": 0, "PSAS": 0}


def test_duplicate_bridge_record_increments_counts_only() -> None:
    records: list[InputRecord] = [
        (Business.SL, ("npi1", "ncpdp1", "dea1")),
        (Business.MH, ("npi2", "ncpdp2", "dea2")),
        (Business.SL, ("npi1", "ncpdp2", None)),
        (Business.SL, ("npi1", "ncpdp2", None)),
    ]
    state = _run_case(
        "Case C6 - duplicate bridge",
        "Repeating the same bridge record should increase counts while sets stay deduplicated.",
        records,
    )

    snapshots = _cluster_snapshot(state)
    assert len(snapshots) == 1
    assert snapshots[0]["npi"] == ["npi1", "npi2"]
    assert snapshots[0]["ncpdp"] == ["ncpdp1", "ncpdp2"]
    assert snapshots[0]["dea"] == ["dea1", "dea2"]
    assert snapshots[0]["customer_record_counts"] == {"SL": 3, "MH": 1, "ERx": 0, "PSAS": 0}


def test_additional_unrelated_record_stays_separate_after_merge() -> None:
    records: list[InputRecord] = [
        (Business.SL, ("npi1", "ncpdp1", None)),
        (Business.MH, ("npi2", "ncpdp2", "dea2")),
        (Business.SL, ("npi1", None, "dea2")),
        (Business.MH, ("npi9", "ncpdp9", "dea9")),
    ]
    state = _run_case(
        "Case C7 - merged cluster plus unrelated cluster",
        "First three records merge into one cluster; fourth should create a separate cluster.",
        records,
    )

    snapshots = _cluster_snapshot(state)
    assert len(snapshots) == 2
    assert snapshots[0]["npi"] == ["npi1", "npi2"]
    assert snapshots[1]["npi"] == ["npi9"]


def test_next_cluster_id_continues_to_advance_after_merges() -> None:
    records: list[InputRecord] = [
        (Business.SL, ("npi1", "ncpdp1", None)),
        (Business.MH, ("npi2", "ncpdp2", None)),
        (Business.SL, ("npi1", "ncpdp2", None)),
        (Business.MH, ("npi5", "ncpdp5", "dea5")),
    ]
    state = _run_case(
        "Case C8 - id counter behavior",
        "Cluster IDs should remain unique/ascending; next id should advance even when merges happen.",
        records,
    )

    assert sorted(state.cluster_id_to_cluster) == [1, 4]
    assert state.next_cluster_id == 5


