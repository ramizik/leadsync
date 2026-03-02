# Database Ruleset

## Schema Decisions
- Fewer than 3 tightly-coupled new columns → extend existing table.
- New entity with own lifecycle, or more than 3 columns → new table.
- Relationship / junction data → always a join table, never a JSON column.

## Query Standards
- No raw SQL strings — all queries through ORM or parameterized builder.
- Indexes required on every foreign key and any column used in WHERE/ORDER BY at scale.
- Migrations must be reversible (include `down` migration).

## Ownership
- Alice owns the database layer. All tickets touching schema require Alice's review before merge.
- Default storage assumption: PostgreSQL relational patterns, not document-oriented.

## Testing
- Test data must be isolated per test — no shared fixtures that mutate shared state.
- Use transactions that roll back after each test, not truncate.
- At least one test per migration verifying the schema change is correct.

## Non-Negotiables
- No `SELECT *` in application queries — enumerate columns explicitly.
- No schema changes in application startup code — migrations only.
