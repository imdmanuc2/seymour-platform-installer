# Operation Engine

SPI operations are first-class lifecycle records with a stable schema.

Each operation records:

- operation ID
- product and action
- adapter
- dry-run state
- created, started, and completed timestamps
- duration
- current step
- step outcomes
- final structured outcome
- evidence timeline

## Commands

```bash
spi operation summary <operation-id>
spi operation latest [product-id]
spi operation timeline <operation-id>
```

Package 006 remains dry-run only.
