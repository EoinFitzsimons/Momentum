Event contract specification
============================

Core principles
- Events are versioned JSON objects with `event_id`, `event_type`, `race_id`,
  `timestamp`, and `payload` fields.
- Ordering guarantee: per-race monotonic by `lap_number`. Producers should
  ensure events are emitted in non-decreasing lap order. Consumers must be
  resilient to at-least-once delivery.
- Delivery semantics: recommend at-least-once with idempotency token on
  `event_id` to allow deduplication.

Common event schema references
- SRS/event_schemas/lap_complete.schema.json
- SRS/event_schemas/overtake.schema.json
- SRS/event_schemas/incident.schema.json

Versioning
- Use semantic versioning for event contract versions (e.g., v1.0.0) and
  include `schema_version` at top-level in each event.

Testing
- Add producer contract tests that assert produced events validate against
  the JSON Schemas in `SRS/event_schemas/`.
