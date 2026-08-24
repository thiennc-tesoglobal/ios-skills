# Behavioral A/B Evaluation

This is the repeatable output-quality check for the focused notification and
StoreKit refactor. It compares the last known baseline commit with the
candidate using the same model, prompt, scenario order, and timeout.

## Baseline and candidate

- Baseline: `e9059f3` (`refactor: streamline notification and StoreKit skills`)
- Candidate: the commit under test
- Scenarios: APNs Simulator boundary and service-extension exact-once completion
  use `push-notifications`; App Review payment rules and StoreKit Test API
  separation use `storekit`.
- Runner: `.github/scripts/behavioral_ab.py`

The runner captures raw model output for human scoring. It does not claim that a
static link/schema validator is a behavioral eval, and it reports an explicit
`unavailable`/`partial` status when a model runner is missing or unauthenticated.

## Run locally

```sh
old_dir=$(mktemp -d /tmp/ios-skills-ab-old.XXXXXX)
new_dir=$(mktemp -d /tmp/ios-skills-ab-new.XXXXXX)
git archive e9059f3 | tar -x -C "$old_dir"
rsync -a --exclude='.git' ./ "$new_dir/"
python3 .github/scripts/behavioral_ab.py \
  --old-root "$old_dir" \
  --new-root "$new_dir" \
  --output /tmp/ios-skills-behavioral-ab.json
```

Authenticate the configured runner first. For Claude Code, run `/login` in a
trusted interactive session, then rerun the command. To run the same scenarios
with Codex instead:

```sh
python3 .github/scripts/behavioral_ab.py \
  --provider codex \
  --model gpt-5.4 \
  --old-root "$old_dir" \
  --new-root "$new_dir" \
  --output /tmp/ios-skills-behavioral-ab-codex.json
```

Both backends run without session persistence and with read-only filesystem
access. Use
`--allow-unavailable` only when recording a machine without model access.

Each built-in scenario selects its own skill. Pass `--skill push-notifications`
or `--skill storekit` only for a focused run that intentionally overrides all
scenario routing. Pass `--scenario <id>` to retry one case without rerunning
completed scenarios; repeat the option to select more than one case.

## Scoring

For each side, score 0–2 for coverage, correctness, and actionability. Record
missed claims separately. A candidate is accepted only when it has no new
materially incorrect claim and does not lose a required boundary; a higher
score is useful evidence but not a substitute for official-source review.

## Recorded results

- Codex `gpt-5.4`, baseline `e9059f3` versus `v1.1.0`: [raw report](results/behavioral-ab-codex-v1.1.0.json) and [blind benchmark](results/behavioral-ab-benchmark-v1.1.0.json).
- Codex `gpt-5.4`, baseline `v1.1.0` versus the entrypoint/reference compaction candidate: [raw report](results/behavioral-ab-compaction-phase5.json) and [blind benchmark](results/behavioral-ab-compaction-benchmark-phase5.json). Both sides scored 18/18 with no new materially incorrect claims.
