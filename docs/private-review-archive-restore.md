# Restore a private AITM review archive

The November 26, 2026 archive preserves review inputs, reviewer outputs, and experiment checkouts from `aitm-workspace/review/`. It is stored locally under `~/.local/share/aitm/private-review-archives/` in the `review-2026-11-26.*` folder. Keep the archive and extracted files in private storage. They contain raw review evidence and Git configuration.

## Restore the files and Git history

Use macOS with Bash, `zstd`, `tar`, `shasum`, Python 3, and Git available. Allow about 35 GiB for a full extraction. Open the archive folder in a terminal and run the following. It verifies the compressed parts and extracts them into a new private directory inside the archive folder.

```bash
(
  set -euo pipefail
  umask 077
  shasum -a 256 -c SHA256SUMS
  shasum -a 256 -c upstream-codex-objects.sha256

  original_review="$(python3 -c 'import json; print(json.load(open("cleanup-result.json"))["review_root"])')"
  restore_dir="$(mktemp -d "$PWD/restore.XXXXXX")"
  printf 'Restoring into %s\n' "$restore_dir"

  extract_part() {
    zstd -dc "$1" | tar --acls --xattrs --fflags -xpf - -C "$restore_dir"
  }
  extract_part parts/review-root.tar.zst
  for part in parts/*.tar.zst; do
    if [ "$part" != parts/review-root.tar.zst ]; then
      extract_part "$part"
    fi
  done
  extract_part upstream-codex-objects.tar.zst

  python3 restore-git.py inventory.json "$original_review" "$restore_dir"
  printf 'Restored review checkouts are under %s/review\n' "$restore_dir"
)
```

Keep the extracted `objects/` and `objects-upstream-codex/` directories beside `review/`. The relocation script redirects Git's alternate object stores and nested worktree links into the restored copy. The supplemental Codex object store supplies the pinned public objects required by an originally blob-filtered clone. The recovered repositories were verified without fetching. Replaying old review commands may require reinstalling the relevant tools or signing in again.

## Verify the archive records

The archive includes `byte-restore-results.txt` for the file comparisons, `git-restore-verification.json` for the restored Git tips, and `receipt-restore-verification.json` for review files matched to committed receipt hashes. `retention-audit.txt` records the original review inventory. The detailed file comparison manifests are in `source-verification-manifests.tar.zst` with a separate checksum file.
