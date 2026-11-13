"""Recompute retained shadow decisions without an API token or a network call."""
import json
from pathlib import Path
import sys

import ci_advisory as ci


class RecordedProvider:
    def __init__(self, responses):
        self.responses = responses

    def document(self, endpoint):
        return self.responses[endpoint]

    def pages(self, endpoint, _):
        return self.responses[endpoint]


def main():
    records = json.loads(Path(sys.argv[1]).read_bytes())
    for scenario in ("historical", "missing_artifact"):
        record = records[scenario]
        replay = ci.observe(RecordedProvider(record["responses"]), shadow=True)
        if replay != record["decision"]:
            raise SystemExit(f"{scenario} differs from recorded result")
        print(f"{scenario}: {replay['status']}")


if __name__ == "__main__":
    main()
