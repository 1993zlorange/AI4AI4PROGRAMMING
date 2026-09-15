# Local rollback — AI4PROGRAMMING Template v0.1.0

## Scope

This release is local only. No external service, registry, deployment, or repository state was changed.

## Rollback procedure

1. Stop distributing or using `ai4programming-template-v0.1.0`.
2. Retain this directory and its `MANIFEST.sha256` as the release audit record.
3. Create a superseding release directory for the corrected version; do not overwrite this version directory.
4. If removal is explicitly authorized, move this exact version directory to an approved archive location and update the formal release record with the disposition.

## Recovery limitation

Because there is no external publication target, rollback cannot revoke copies that may already have been manually copied outside this workspace.
