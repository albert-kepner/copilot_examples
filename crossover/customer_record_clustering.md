# Customer Record Clustering Across McKesson Businesses

## Objective

We want to identify customers based on which McKesson businesses they are customers of:

| Abbreviation | Business |
|---|---|
| SL | Supply Logix |
| MH | Macro Helix |
| ERx | Enterprise Rx |
| PSAS | Pharmaceutical Solutions and Services |

## Customer Identifiers

We use three identifier types:

- **NCPDP**
- **NPI**
- **DEA**

## Linking Rules

Customer records can be be linked by:

1. Shared identifier values across records.
2. Different identifier types appearing within the same business record.

## Clustering Approach

### Initial State

- Conceptually, each business record containing at least one non-null identifier starts as its own cluster.

### Expansion Rules

- Link identifiers that appear together in a business record.
- Continue merging connected clusters until no additional merges are possible.
- At completion, each unique identifier belongs to exactly one cluster.

## Cluster Bookkeeping

For each cluster store:

- Participating McKesson businesses (SL, MH, ERx, PSAS)
- Record count by business
- All NCPDP IDs
- All NPI IDs
- All DEA IDs

Example business-count mapping:

```python
{
    "SL": count,
    "MH": count,
    "ERx": count,
    "PSAS": count
}
```

## Global Bookkeeping

### Identifier Indexes

One dictionary per identifier type:

```python
ncpdp_to_cluster
npi_to_cluster
dea_to_cluster
```

### Cluster Registry

```python
cluster_id_to_cluster
```

Maps cluster IDs to cluster objects.

## Rough Algorithm Draft 2

### Initialization

- Assign the first business record to its own cluster.

### Record Processing

For each business record, and continuing with all 4 business units:

- If no identifiers match an existing cluster, create a new cluster.
- If exactly one cluster matches, add the record's identifiers to that cluster, by merging.
- If two or more clusters match, merge those clusters and also merge the current record's identifiers.

### Index Maintenance

Whenever clusters are created or merged:

- Update all identifier indexes.
- Ensure every identifier points to the correct cluster.
- Invariant: After each record is merged, every unique identifier value should exist in eactly one cluster.

### Cluster IDs

- Each new cluster receives a unique cluster ID.

## Core Operations

1. New cluster creation
2. Cluster ID assignment
3. Cluster merging

## Expected Outputs

For each cluster determine:

- Participating McKesson businesses
- Record counts by business
- Complete NCPDP identifier set
- Complete NPI identifier set
- Complete DEA identifier set
- Stable cluster identifier


# Program Design

## Module: cluster_state

contains enum Business
with values named SL, MH, ERX, PSAS

Contains class ClusterState


### Data elements:

next_cluster_id: int ## initial value 1; used to assign unique ascending values for each new cluster.

The following 3 dicts each map from an identifier value to its current cluster_id.

npi_to_cluster: dict[str, int]
ncpdp_to_cluster: dict[str, int]
dea_to_cluster: dict[str, int]

The following dict maps from cluster ids to the Cluster object.

cluster_id_to_cluster: dict[int, Cluster]

### Operations

get_next_cluster_id() -> int

- Returns the next ascending integer each time it is called. Used when assigning an id to a new cluster.

add_record ( business: Business, record_ids: tuple[str, str, str])

- The tuple record_ids is always in the order NPI, NCPDP, DEA
- Any ids for a record can be None, but not all for a given record.
- add_record creates a new cluster for the given record and then attempts to merge
that cluster with any clusters which match. 
- If the new record does not match any existing cluster, the 4 dicts above are
updated to record the new cluster, which currently stands alone.
- With 3 ids, as many as 3 existing clusters could match.
To merge, one of the existing clusters is selected to absorb the others. 
The other clusters are merged, one at a time, into the surviving cluster. The actual merge 
operation always acts on a pair of clusters.
All of the ids from the
absorbed clusters are added to the surviving cluster. The absorbed clusters are removed from the cluster_id_to_cluster dict.
For all ids moved to a new cluster, the 3 dicts like npi_to_cluster are updated with the surviving cluster id.
At the conclusion of merging every unique id should exist in exactly one cluster. As an additional side effect of merging,
the customer_record_counts (dicts) of the merging cluster are added into the customer_record_counts  of the surviving cluster.
Therefore the customer_record_counts keep track of how many records from each business have been combined into the resulting cluster.




## Module: cluster

Contains class Cluster

Date elements:

cluster_id: int ## identifies this cluster

customer_record_counts: dict[str, int]

- counts the number of customer records for each business that fall into the current cluster

Like
```python
{
    "SL": count,
    "MH": count,
    "ERx": count,
    "PSAS": count
}
```

npi_set: set[str] ## all NPI ids in the current cluster

ncpdp_set: set[str] ## all NCPDP ids in the current cluster

dea_set: set[str] ## all DEA ids in the current cluster 

Operations:

__init__ ( business: Business, record_ids: tuple[str, str, str])

- Assume that a cluster is always initialized with ids from a single business record. From there
the cluster will get merged with other clusters if ids match.

