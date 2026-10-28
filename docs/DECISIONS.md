# DroidLens project decisions

- We keep the database in `~/.droidlens/sessions/<id>/session.db` by default and allow an explicit override via `--work-dir`. This keeps every session self-contained and makes audit and export easier.
- We prefer a library-first design: every CLI command is a thin wrapper over explicit `DroidLens` API calls, not independent logic. That keeps the static/dynamic/adaptive surfaces consistent and testable.
- We use a single-owner `BackendExecutor` thread for all Androguard calls to avoid PyO3 thread-affinity crashes when the Frida bridge and adaptive loop also run in parallel.
- We treat Gemini as the default AI provider and keep the provider implementations behind a provider-protocol boundary, so local models and remote APIs can share the same code path.
- We keep the repo intentionally minimal in milestone 1 while keeping extension points open for the later static/dynamic/adaptive milestones.
