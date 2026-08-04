# Rollback Execution Engine

Package 009 executes transaction rollback plans in dry-run mode.

Each rollback item moves through `planned`, `rolling-back`, `paused`, and
`rolled-back`. Rollback can resume after interruption, preserves completed
rollback items, and prevents duplicate rollback work.
