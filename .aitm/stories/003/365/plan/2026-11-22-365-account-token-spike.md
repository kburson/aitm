# #365 Account-token attribution spike

**Disposition: HOLD.** The dedicated-App design cannot use the exact existing account token. It would require an App installation credential. Same-token operation requires a revised storage trust contract before the publisher can ship.

## Live probe

The current GitHub CLI account token authenticated as `kburson`, type `User`. On [isolated issue #420](https://github.com/kburson/aitm/issues/420), the existing publisher adapter submitted its actual body-only PATCH with that token. The body read back byte for byte. The GraphQL editor was `kburson` (`User`) at 2026-11-22T13:20:36Z. The current publisher reader rejected the decisive body with `advisory edit was not attributed to the dedicated App`. The isolated issue was then closed and its closure verified. The production issue #418 read back identically before and after the probe, including the uninitialized body and null editor.

The existing token also received HTTP 401 from the App-authenticated `GET /app` endpoint. GitHub documents that a GitHub App user token attributes activity to a user and an installation token attributes it to the App. The current account can own an App without creating another GitHub user, but the App must authenticate separately to make App-attributed edits. [GitHub user access tokens](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-user-access-token-for-a-github-app) · [GitHub App installation authentication](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app-installation).

No new credential or App was provisioned. The App installation route was not live-tested in this spike. The earlier [#158 merge-fence trial](https://github.com/kburson/aitm/issues/158) also left independent role enforcement unqualified, on a different mutation path. This probe answers only the existing-token advisory path. #365 stays in Dev and PR #419 stays draft.
