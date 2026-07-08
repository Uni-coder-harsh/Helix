---
owner: "@harsh"
version: "0.1.0"
status: "Draft"
last_updated: "2026-07-05"
reviewer: "@harsh"
dependencies: []
---

# Plugin Framework

This document outlines the design specification for extending Helix via modular plugins.

> [!NOTE]
> Detailed interface types and lifecycles will be defined in **Phase 2: Architecture**.

## Interface Design

Plugins extend functionality by implementing standard lifecycle methods:

```python
class HelixPlugin:
    def on_load(self) -> None:
        """Called when plugin is registered."""
        pass

    def on_unload(self) -> None:
        """Called when plugin is unregistered."""
        pass
```
