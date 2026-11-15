# #323 Evidence reproduction

Use the released planning commit and verify SHA256SUMS first. The zip contains native request, run, attempt, check, job, artifact, ruleset, PR, branch and production snapshots, runner setup and execution logs, independently collected inventories, control outputs, and the native release receipt. Digest strings in the qualification summary refer to downloaded bytes.

1. From the planning plan directory, check the hashes and archive. Copy the recipe contents into a fresh scratch directory and extract the records beside verify_recovery.py. Fetch the exact public source without changing any production branch.

~~~sh
shasum -a 256 -c SHA256SUMS
unzip -t rehearsal-evidence.zip
recovery_scratch=$(mktemp -d)
cp -R recipe/. "$recovery_scratch/"
unzip -q rehearsal-evidence.zip -d "$recovery_scratch"
cd "$recovery_scratch"
mkdir subject
git -C subject init --quiet
git -C subject fetch --no-tags --depth 1 https://github.com/kburson/aitm.git 9de9dbbec4053b95cfab5e005cd876c667f71e10
git -C subject checkout --quiet --detach FETCH_HEAD
git -C subject rev-parse HEAD HEAD^{tree}
~~~

The expected tree is d551e285f8c15c98ec7285bbf43f78c59d345756. The reader and verifier import the retained exact production observer, evidence shape and policy from this detached checkout.

2. Reproduce the independent positive and off-host controls at the retained verification instant. The command reads then regenerates records/control-results.json in the disposable replay directory. It never calls GitHub or releases a hold.

~~~sh
python3 replay_controls.py
~~~

3. Optionally regenerate both ordered inventories on macOS ARM64 with uv 0.10.6 and Python 3.13.9. Copy the two retained reference JSON documents aside first, rerun collection, then compare them bytewise. Full execution ran on GitHub macOS/APFS and the retained logs record the tool download, lock, both whole profiles and all phase/child outcomes.

~~~sh
cp records/reference-product.json /tmp/aitm-323-product-before.json
cp records/reference-helpers.json /tmp/aitm-323-helpers-before.json
bash collect-reference.sh
cmp /tmp/aitm-323-product-before.json records/reference-product.json
cmp /tmp/aitm-323-helpers-before.json records/reference-helpers.json
~~~

4. Check the signed operator admission and separate acknowledgment using the preserved public rehearsal key.

~~~sh
ssh-keygen -Y verify -f records/operator.allowed_signers -I rehearsal-operator -n aitm-323-missed-slot -s records/dispatch/authorization.json.sig < records/dispatch/authorization.json
ssh-keygen -Y verify -f records/operator.allowed_signers -I rehearsal-operator -n aitm-323-missed-slot -s records/operator-acknowledgment/acknowledgment.json.sig < records/operator-acknowledgment/acknowledgment.json
~~~

5. Independently compare native GitHub REST readbacks for exact attempts 1 and 2, the artifact metadata attached to the run, and the two native rule suites. The latest run will show the intentionally replayed attempt 2 after acknowledgment. Attempt 1's accepted snapshot remains a historical observation. After the deliberate replay the provider listing was empty and artifact 14173500281 was unavailable via its original endpoint. Use the archive and provider digest saved before attempt 2.

~~~sh
gh api repos/kburson/aitm-missed-slot-323/actions/runs/43741833227/attempts/1
gh api repos/kburson/aitm-missed-slot-323/actions/runs/43741833227/attempts/2
gh api repos/kburson/aitm-missed-slot-323/actions/runs/43741833227/artifacts
gh api repos/kburson/aitm-missed-slot-323/rulesets/rule-suites/5132918857
gh api repos/kburson/aitm-missed-slot-323/rulesets/rule-suites/5132983767
~~~

The setup, dispatch, hold probes, acknowledgment and native replay commands are retained to document the exact sequence that made these records. They write to a disposable target. Their hardcoded repository, time window, key and run are unique to this rehearsal. The first setup was abandoned before dispatch after production trunk advanced. Re-pinning used a normal lab PR and a fresh window, with the ordinary lab protection active during setup. There was no abbreviated production test run or production recovery dispatch. Production reads are captured separately. The ephemeral private key is outside the evidence archive.

The report and summaries describe collection and execution of the production scheduled product/helper scope. The production PR-specific lint, coverage, wheel smoke, status-admission and review sequence is governed separately by #103.
