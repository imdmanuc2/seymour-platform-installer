# SPI Repository Structure

The Seymour Platform Installer separates lifecycle orchestration,
platform behavior, product definitions, plugins, and runtime state.

## Layout

```text
seymour-platform-installer/
├── bin/
│   └── spi
├── docs/
├── lib/
│   ├── core/
│   ├── adapters/
│   ├── plugins/
│   ├── lifecycle/
│   └── state/
├── products/
├── tests/
├── state/
└── VERSION
