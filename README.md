# notifications-workspace

Notifications workspace.

## Sibling repos

The repos listed in `scripts/sync_repos.py` are cloned as top-level directories and gitignored here; each remains an independent git repo.

```sh
scripts/sync_repos.py                          # clone missing, fast-forward all to primary branch
scripts/sync_repos.py ds-notification-service  # just one
```

Existing repos with local changes are stashed (`git stash list`) and switched to their primary branch before fast-forwarding.
