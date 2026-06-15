# .agency/ — central graph DB

The agency engine's bi-temporal provenance graph lives here as
`session.db`. Per Spec 020 the DB is **committed to git** so team
learnings + observation reflections persist across clones and
branch checkouts.

## Inspect

```bash
sqlite3 .agency/session.db
.tables
SELECT * FROM nodes LIMIT 5;
```

## Reset

```bash
rm .agency/session.db
python -m agency.install     # regenerates an empty DB on next engine start
```

## Backup

```bash
sqlite3 .agency/session.db ".backup .agency/backup-$(date +%F).db"
```

## Merge conflicts

The DB is binary; git can't auto-merge. Recovery: each branch can
export to JSON via `dogfood.export` (Spec 020 deliverable), then both
exports replay against a fresh DB on the merged commit.

See `Plan/020-central-graph-db/spec.md` for the full design.
