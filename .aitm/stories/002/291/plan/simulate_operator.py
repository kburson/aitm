"""Use the reviewed operator-role path on the synthetic #291 target only."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = "kburson/aitm-stl-rehearsal-291"
REPO_ID = 1458821034
OPERATOR = 1082467


def api(path, *args):
    return json.loads(subprocess.check_output(["gh", "api", path, *args]))


def save(name, data):
    (ROOT / name).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def verify_nomination():
    nomination = ROOT / "repair-nomination.json"
    record = json.loads(nomination.read_bytes())
    review = (ROOT / "repair-review.md").read_text()
    assert "ACCEPTED" in review and sha256(nomination.read_bytes()).hexdigest() in review
    assert record["repository"] == REPO and record["pr"] == 1
    assert record["target"] == "trunk" and record["operator_id"] == OPERATOR
    prefix = f"repos/{REPO}"
    assert api(prefix)["id"] == REPO_ID and api("user")["id"] == OPERATOR
    branch = api(f"{prefix}/branches/trunk")
    assert branch["protected"] and branch["commit"]["sha"] == record["base"]
    pull = api(f"{prefix}/pulls/1")
    assert pull["state"] == "open" and pull["head"]["sha"] == record["head"]
    assert pull["base"]["ref"] == "trunk" and pull["base"]["sha"] == record["base"]
    run = api(f"{prefix}/actions/runs/{record['run_id']}/attempts/{record['attempt']}")
    assert (run["event"], run["status"], run["conclusion"]) == ("pull_request", "completed", "success")
    assert run["head_sha"] == record["head"] and run["repository"]["id"] == REPO_ID
    probed = api(f"{prefix}/actions/runs/{record['ordinary_probe']}")
    assert probed["conclusion"] == "success"
    hold = api(f"{prefix}/rulesets/{record['hold_ruleset']}")
    normal = api(f"{prefix}/rulesets/{record['normal_ruleset']}")
    assert hold["enforcement"] == normal["enforcement"] == "active"
    assert hold["bypass_actors"] == [{"actor_type": "User", "actor_id": OPERATOR, "bypass_mode": "pull_request"}]
    assert normal["bypass_actors"] == []
    assert hold["conditions"]["ref_name"] == normal["conditions"]["ref_name"] == {
        "exclude": [], "include": ["refs/heads/trunk"],
    }
    assert {rule["type"] for rule in normal["rules"]} == {"pull_request", "required_status_checks"}
    rules = api(f"{prefix}/rules/branches/trunk")
    assert {row["ruleset_id"] for row in rules} == {hold["id"], normal["id"]}
    save("effective-before-repair.json", rules)
    return record, prefix


def main():
    review_path = ROOT / "repair-review.md"
    record, prefix = verify_nomination()
    result = api(f"{prefix}/pulls/1/merge", "--method", "PUT", "-f", f"sha={record['head']}", "-f", "merge_method=merge")
    assert result["merged"]
    save("native-operator-merge.json", result)
    move = api(f"{prefix}/git/commits/{result['sha']}")
    assert move["tree"]["sha"] == record["tree"]
    assert [p["sha"] for p in move["parents"]] == [record["base"], record["head"]]
    merged = api(f"{prefix}/pulls/1")
    assert merged["merged"] and merged["merged_by"]["id"] == OPERATOR
    assert merged["merge_commit_sha"] == result["sha"]
    assert merged["head"]["sha"] == record["head"]
    assert api(f"{prefix}/branches/trunk")["commit"]["sha"] == result["sha"]
    saved = {
        "scope": "simulated operator on disposable target",
        "nomination": record,
        "repair_review_sha256": sha256(review_path.read_bytes()).hexdigest(),
        "merge": result["sha"], "merged_at": merged["merged_at"],
        "operator_id": merged["merged_by"]["id"],
    }
    save("verified-repair.json", saved)
    print(json.dumps(saved, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
