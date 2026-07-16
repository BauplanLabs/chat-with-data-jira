# Writing the pull request description

Merging the PR publishes tables to production `main`. The reviewer is a data engineer who must see everything the merge does and be able to check it without reverse-engineering the code. Build every section from Bauplan introspection (the branch diff, table metadata, job status), not from memory of what you think you did.

Two rules override everything else:

1. **Every table the merge publishes appears in the description, with its row count.** Derive the list from `bauplan branch diff main <your-branch>`. The classic failure is describing only the gold table while an imported or intermediate table silently rides along.
2. **Never reproduce pipeline code.** The code is the PR diff; the description covers what the diff cannot show, namely the data.

The PR body has five sections, in this order. Each one maps to a field of the structured output the workflow asks for.

## Summary

One short paragraph: what the pipeline computes, which tables it reads, which tables it publishes. No process narration.

## Lineage

First name the source tables explicitly in prose, then draw the flow as a Mermaid diagram. GitHub renders `mermaid` fences in PR bodies, so the reviewer sees a picture, not a list.

- `flowchart LR`, one node per source table and per model.
- Sanitize node ids by replacing every non-word character with `_`; keep the real name as the label.
- Edges follow reads: source table to silver model, silver to gold.
- Highlight the materialized output tables with a `classDef` so the reviewer sees at a glance where data lands.

Example:

````
```mermaid
flowchart LR
    bronze_orders["bronze.orders"]
    orders_clean["orders_clean"]
    revenue_by_region["revenue_by_region"]:::output
    bronze_orders --> orders_clean --> revenue_by_region
    classDef output fill:#dcfce7,stroke:#16a34a,color:#14532d;
```
````

## Testing

State plainly what was verified and how:

- Whether expectations ran with strict mode (`--strict on`, otherwise they are skipped) and whether they all passed.
- What each expectation covers, in plain words ("no null order ids", "net revenue is non-negative"), not function names.
- Any ad-hoc check queries you ran on the branch, and what they showed.

## Metrics

A markdown table with one row per published table from the branch diff: row count, column count, size. Read these from table metadata (`bauplan table get <namespace>.<table> --ref <branch>` or `client.get_table`); metadata is free, never run `COUNT(*)` for this. Then report null counts for the gold table's key columns, from a single profiling query on the branch.

## Info

How the reviewer verifies the work themselves:

- The Bauplan data branch you materialized on. Leave it in place; it is the review artifact.
- The exact commands to run, with the real branch and table names filled in:

```
uv run bauplan query "SELECT * FROM <gold_table> LIMIT 10" --ref <branch>
uv run bauplan run --dry-run --strict on
```

The first inspects the materialized result, the second revalidates the pipeline from the PR checkout (on the reviewer's own branch, never `main`).

Close with a Problems note: errors, blockers, or deliberate deviations from the issue, or "None".
