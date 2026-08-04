# Transaction Engine

Package 008 adds dry-run transaction and checkpoint records to SPI lifecycle
operations.

Each step is prepared, executed, and committed. Interrupted transactions retain
their last committed checkpoint and a generated rollback plan. Resume continues
from the first incomplete lifecycle step while preserving Package 007 retry
behavior.
