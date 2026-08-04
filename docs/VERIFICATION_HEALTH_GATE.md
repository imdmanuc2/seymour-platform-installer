# Verification & Health Gate Engine

An SPI lifecycle operation is successful only after its post-action health gate passes.

The gate checks lifecycle completion, plugin results, transaction checkpoints, and dry-run safety. A failed gate marks the operation failed, marks the transaction `verification-failed`, preserves the rollback plan, and records evidence.
