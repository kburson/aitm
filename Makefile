PYTHON_BIN ?= python3.13
export PYTHON_BIN

.PHONY: dashboard
dashboard:
	@set -eu; \
	"$$PYTHON_BIN" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 13) else "Python 3.13 or later is required")'; \
	git fetch origin refs/heads/planning:refs/remotes/origin/planning; \
	planning_sha=$$(git rev-parse --verify refs/remotes/origin/planning); \
	cutoff_utc=$$(date -u +%Y-%m-%dT%H:%M:%SZ); \
	output=$$(mktemp -d "$${TMPDIR:-/tmp}/aitm-story-dashboard.XXXXXX"); \
	"$$PYTHON_BIN" -m tools.story_dashboard.snapshot \
	  --repo "$$PWD" --commit "$$planning_sha" --as-of "$$cutoff_utc" --output "$$output"; \
	"$$PYTHON_BIN" -m tools.story_dashboard.render \
	  --snapshot "$$output/snapshot.json" --output "$$output/dashboard.html"; \
	printf 'Dashboard: %s\n' "$$output/dashboard.html"; \
	open "$$output/dashboard.html"
