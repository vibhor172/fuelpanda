# Decisions & Assumptions

## Assumptions (from the brief)

1. **Auth is stubbed.** Identity is injected by `get_current_admin` / `get_current_driver`.
2. **One shift per driver per day; one vehicle per allocation per day.**
3. **Order == Delivery.** One order = one destination + many `order_items`.
4. **Hubs & Terminals share one `locations` table** (`type` discriminator).
5. **Allocating a vehicle auto-creates a `SCHEDULED` shift** referencing the allocation.
6. **Incomplete deliveries at shift end** are auto-`FAILED` with reason
   `UNCOMPLETED_AT_SHIFT_END` — no silent inventory change.
7. **GPS accepted only during an `ACTIVE` shift.**
8. **Quantities in gallons, `> 0`; inventory never negative.**
9. **Postgres is the source of truth; Redis is a rebuildable accelerator.**
10. **Releasing a vehicle frees it for re-allocation the same day.**

## Trade-offs

- **DB constraint over app-level locking for blocking.** A `SELECT … then INSERT`
  check races under concurrency. A partial unique index makes the database the single
  arbiter: exactly one `INSERT` wins, the loser gets an `IntegrityError` we translate
  to a clean `409`. The Redis lock (`SET NX EX`) is defense-in-depth — it reduces
  contention and gives early rejection, but correctness never depends on it (it's
  correct even if Redis is down).

- **Pessimistic row locks for inventory.** Completion does `SELECT … FOR UPDATE` on
  the order and on each inventory row, then bumps quantities and flips status in one
  commit. No lost updates; the whole delivery is atomic.

- **Idempotent finalization.** `complete`/`fail` first re-read the order under a row
  lock and reject if it's already `COMPLETED`/`FAILED` (`DeliveryAlreadyFinalized`,
  409). Guards double-submits.

- **Fleet status read model (perf nice-to-have).** Naïve "latest location of all
  active vehicles" is `DISTINCT ON (vehicle_id) … ORDER BY recorded_at DESC` over a
  fast-growing table — O(history). Instead, every GPS ingest write-through updates:
  (1) the Redis hash `fleet:live`, (2) `vehicle:{id}:location`, and (3) the
  denormalized `vehicles.last_*` columns. `GET /fleet/status` is `HGETALL` →
  O(active vehicles), constant in history size. If Redis is cold, we fall back to the
  denormalized DB columns (one indexed pass) — still no history scan. History queries
  stay on the partitioned `gps_locations` table, decoupled from the hot path.

- **Fleet membership.** A vehicle's live-location field is created on its first GPS
  ingest and removed on shift end. We intentionally do **not** insert an empty
  placeholder on shift start (a vehicle with no GPS yet has no location to report);
  the active-shift join provides the DB-side membership for the fallback path.

- **Caching strategy.** Cache-aside (lazy, short TTL) for inventory monitoring;
  write-through for the live-location model. All Redis access lives behind
  `CacheService` / `LockService` so handlers stay storage-agnostic and unit-testable
  with fakeredis.


