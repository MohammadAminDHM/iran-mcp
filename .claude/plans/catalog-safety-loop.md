# Catalog safety loop

Status: prepared, not running.

## Scope and boundaries

- Pattern: sequential; mode: safe; one catalog defect per iteration.
- Starting point: local `main`, with existing uncommitted changes. Preserve those changes;
  do not include them in a checkpoint unless their owner explicitly approves.
- Scope: reproducible correctness and safety issues in `scripts/catalog.py`.
- Never modify generated files by hand, weaken tests, deploy, push, merge, change
  workflow configuration, or use account-modifying tools as part of this loop.
- Use the current model; do not invoke paid experiments or additional agents without approval.

## Iteration

1. Inspect one concrete code path and identify a reproducible defect.
2. Write an isolated regression test and run it; confirm it fails for the intended reason.
3. Apply the smallest correction and rerun the regression test and full offline suite.
4. Run `python scripts/check_counts.py` and `git diff --check`; inspect the complete diff.
5. Report evidence and request human review before any new commit.

## Stop conditions

- Stop after at most three defect iterations, or when no further reproducible defect is found.
- Stop immediately on a failed quality gate that cannot be resolved within two attempts,
  unexpected changes, missing dependencies, ambiguous requirements, or a security-sensitive
  change needing human judgment.
- Do not automatically accept, merge, push, or mark a task complete on behalf of the user.

## Preflight and monitoring

Run from the repository root:

```powershell
git status -sb
python -m unittest discover -s tests -v
python scripts/check_counts.py
git diff --check
$env:ECC_HOOK_PROFILE
```

`ECC_HOOK_PROFILE` must not be `off` or `disabled`. An environment value alone does not
prove hooks are installed or active; verify the OpenCode harness configuration separately.
Review each iteration's status with `git status -sb` and `git diff` and stop manually if
any boundary above is crossed.

No managed loop launcher or recurring scheduler has been verified in this environment.
Until one is available and the dirty working tree has been reviewed, run iterations manually;
do not treat this document as evidence that an autonomous process has started.
