# PR #562 source SAR

Independent read-only Grok 4.7 review began after both hosted workflows passed while the PR was
draft and GitHub confirmed ready-for-review on the exact candidate. Packet SHA-256
`30d10b3c9c9e5091ee8bf50d00b63cbdcdc67f8dd49c20d7fbec8ac48f7889bd`.

[Exact hosted verification](2026-11-27-pr-562-eeada220-verification.md).

## Independent verdict

CHANGES REQUIRED

Base `0a358173354eee4bb09cc98d2e8cbeb286790c45`. Head `eeada22066d699cd0ac64d339721dba4d5c3c881`. Synthetic merge `b2c7175f32c9bb03ebf5e6af74f54142c3c35752`. Tested tree `cbd4d72b93d531f9ab1251df60637c5f23f6e3a0`.

`doctor` in `setup/doctor.py` decides checkout exclusion with `_worktrees(repo, RefIdentity(repo.ref))` where `repo` is `context.repository`. `cli/doctor.py` `handle` opens `Repository(Path.cwd(), "refs/heads/aitm-doctor-probe")`, and `hooks._execute` opens `refs/heads/aitm-hook-probe`, then both pass that object to `_active_installation`. This diff never copies `installation.store.planning_ref` onto that ref. `_guard` does use `installation.store.planning_ref` for commit and pre-push checks. The readiness facet therefore inspects the probe ref: a worktree checked out at the configured planning ref does not add pending `checkout` or the “requires attention” evidence.

`_prepare_worktree` in `setup/init.py` calls `prepare_ignore` and, whenever `HEAD` is `proposal.anchor.code_default_ref`, returns `IGNORE_COMMANDS`. `prepare_ignore` returns false when `ignore_proposal` sees `/.aitm/` already present. `GitHooks.install` emits `git add -- .gitignore` and the ignore commit only when `prepare_ignore` returns true. The bootstrap resume path still prints those commands when the file is unchanged, so the landing instructions are not the exact commands.

`doctor` prints the generic protection sentence only when `context.store.planning_remote is not None`, and then always appends pending `protection` with no `applied`, `already-protected`, or `manual` result and no settings URL. The no-remote branch, including `--local`, reports that hosted protection is not applicable. With no git host provider, init/doctor must print the generic protection instructions as their own readiness facet.

## Agent Cost

| Turn | Cached input tokens | New input tokens | Output tokens | Verified billed cost |
| --- | ---: | ---: | ---: | --- |
| 1 | 2,432 | 16,999 | 20,849 | Unknown |
