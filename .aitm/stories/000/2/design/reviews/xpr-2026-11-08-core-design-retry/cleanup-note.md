# Post-publication cleanup limitation

The accepted XPR public originals, portable response/patch chain and final FUR were verified and published at `1f4d4a354a10dfd173c70cc8421dafd28c25a57a` before cleanup. The app subsequently archived the completed review worktree with its tracked/untracked snapshot. Neither blocked native worktree was archived.

The author requested app archival while the private scratch tar process was still running, rather than awaiting successful creation and byte comparison first. Tar failed when the checkout disappeared during traversal of the cached runtime package. Its restricted partial archive remains readable and contains 21 files from the native review workspace, including protocol, event log, participants, response receipts and provider launch state. Their retained bytes have recorded hashes, but comparison with the removed originals is no longer possible. This is an archive-verification limitation; it is not represented as fully verified preservation of every ignored file.

The independently reconstructable public acceptance record is unchanged. Future cleanup must await private archive completion and byte comparison before requesting app archival. The restricted archive and detailed local evidence remain under the repository common Git directory; no private handles or scratch contents are published here.
