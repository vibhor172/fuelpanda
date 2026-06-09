# Database Design

PostgreSQL 16. Every table inherits `id`, `created_at`, `updated_at` from `BaseModel`.

## ERD (logical)

```
Driver ─1:N─ Shift ─N:1─ VehicleAllocation ─N:1─ Vehicle
                │
                └─1:N─ Order ─1:N─ OrderItem ─N:1─ Product
                          │
                          └─N:1─ Location (HUB | TERMINAL)

Location ─1:N─ Inventory ─N:1─ Product
Vehicle ─1:N─ GpsLocation ─N:1─ Shift
```

## Tables

| Table | Key columns | Constraints / indexes |
|---|---|---|
| `locations` | name, type(HUB/TERMINAL), address, lat, long | index `(type)` |
| `products` | name, code, unit | unique `name`, unique `code` |
| `inventories` | location_id, product_id, quantity_gallons | unique `(location_id, product_id)`; check `quantity_gallons >= 0` |
| `drivers` | name, license_number, phone, status | unique `license_number` |
| `vehicles` | registration_number, capacity_gallons, status, last_lat/long/seen_at | unique `registration_number` |
| `vehicle_allocations` | vehicle_id, driver_id, allocation_date, status | **partial unique** `(vehicle_id, allocation_date) WHERE status='ACTIVE'` and `(driver_id, allocation_date) WHERE status='ACTIVE'` |
| `shifts` | driver_id, allocation_id, shift_date, status, started/ended_at | unique `(driver_id, shift_date)` |
| `orders` | shift_id, destination_id, status, failure_reason, completed_at | index `(shift_id)`, `(status)` |
| `order_items` | order_id, product_id, quantity_gallons | unique `(order_id, product_id)`; check `> 0` |
| `gps_locations` | vehicle_id, shift_id, lat, long, recorded_at | index `(vehicle_id, recorded_at)`, `(shift_id, recorded_at)` |

## Design decisions

- **Partial unique indexes for blocking.** The two hardest rules (vehicle blocking,
  one-shift-per-driver-per-day) are enforced by the database, not by application
  read-then-write logic. Released allocations leave the partial index, so a vehicle
  freed mid-day can be re-allocated the same day.

- **Unified `locations` table.** Hubs and Terminals share one table with a `type`
  discriminator so inventory and order destinations reference a single FK. Trade-off:
  a nullable-friendly shared shape vs. two tables + polymorphic FKs. Chosen for FK
  simplicity given identical columns.

- **Denormalized `vehicles.last_*` columns.** A DB-side fallback for fleet status so
  the "latest location" path never scans `gps_locations`. Updated on every GPS ingest.

- **`gps_locations` as an append-only time series.** Indexed on `(vehicle_id, recorded_at)`
  for partition-pruned history scans. In production this table is a candidate for
  range partitioning by `recorded_at` (daily/monthly) for cheap retention — the schema
  is written so that change is additive.

- **Numeric for quantities/coords**, not float — exact gallons, no rounding drift.
