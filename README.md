# droidlens

A production-grade Python toolkit for authorized Android reverse engineering and pentesting.

This repository is being built in milestone order from the project specification. The current branch contains the core scaffold for milestone 1: configuration, session database, adapter protocol, the thread-affinity backend executor, and the CLI shell for `open`, `info`, `sessions`, and `resume`.

Quick usage:

```bash
pip install -e .
droidlens --version
droidlens open /path/to/app.apk --name demo
```

The project is intentionally structured to make static, dynamic, and adaptive analysis modes first-class and independently usable.
