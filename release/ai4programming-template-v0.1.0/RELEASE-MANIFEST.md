# AI4PROGRAMMING Template v0.1.0 — Release Manifest

## Release identity

- Package: `ai4programming-template-v0.1.0`
- Type: local template release
- Version: `v0.1.0`
- License: MIT
- Release date: 2026-09-13
- External actions: none — no upload, deployment, restart, signing, push, or external publication was performed.

## Included content

| Path | Purpose | Included |
| --- | --- | --- |
| `AGENTS.md` | Root governance and release rules | Yes |
| `README.md` | Template overview and setup guidance | Yes |
| `LICENSE` | MIT license text | Yes |
| `projectname/project/` | Engineering template, tests, configuration examples, documentation, and declarative release skeleton | Yes |
| `MANIFEST.sha256` | SHA-256 integrity list for this package | Yes |
| `ROLLBACK.md` | Local rollback procedure | Yes |

## Exclusions

- `projectname/achieve/00-项目管理/`: internal requirements, supervision, logs, quality, costs, and change records.
- Runtime logs, cache files, `__pycache__`, temporary output, secrets, real data, uploads, and environment files.
- Product code, product artifacts, deployment credentials, external release metadata, and claims of product acceptance.

## Verification

1. Validate the source governance records with `python projectname/project/scripts/f001_governance_validate.py --project-root . --check` from the source project root.
2. Verify every file listed in `MANIFEST.sha256` with SHA-256 before reuse.
3. Review `README.md`, `LICENSE`, and `projectname/project/README.md` before deriving a product project.

## Known limitations

This is a scaffold only. It has no business requirements, production API, UI, database schema, lockfile, CI configuration, product build artifact, independent product QA, or deployment target.
