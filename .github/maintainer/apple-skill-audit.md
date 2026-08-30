# Apple Skill Audit

Audit Apple-platform skills as agent instructions, not as general documentation. Ground findings in repository evidence and current primary sources.

## Audit modes

- **Focused skill:** inspect one skill, references, scripts, neighboring boundaries, and evals.
- **Collection:** inspect inventory, discovery cost, overlap, metadata synchronization, validation, and coverage.
- **Release:** run the collection audit plus package, version, install, credential, and release-gate checks.

Keep an audit read-only unless implementation is explicitly requested.

## Preflight

1. Read the repository instructions and current Agent Skills authoring standards listed there.
2. Inspect Git status and preserve user-owned changes.
3. Identify the exact skills, platform/toolchain claims, package surfaces, and eval formats in scope.
4. Verify API names, availability, platform behavior, and beta-sensitive claims against current Apple documentation, SDK headers, Swift releases, or WWDC transcripts.
5. Separate confirmed defects from recommendations and version-sensitive uncertainty.

Do not infer that every Apple framework needs its own skill. Add or split a skill only when real tasks show a coherent capability and a routing benefit.

## Skill checks

### Discovery and boundaries

- Folder and frontmatter `name` follow the Agent Skills specification.
- `description` states what the skill handles and when it should activate.
- Neighboring skills have boundaries that prevent common false positives.
- Discovery text remains concise enough for the full installed catalog.

### Instructions and references

- `SKILL.md` contains shared workflow, non-obvious constraints, and routing.
- Conditional API detail, examples, and long recipes live in directly linked references.
- The skill selects a modern default while respecting deployment targets.
- Absolute rules correspond to real safety, correctness, or authorization constraints.
- References are reachable, focused, and not duplicated in the entrypoint.

### Technical evidence

- API symbols, availability, entitlement, privacy, lifecycle, concurrency, and platform claims match primary evidence.
- Legacy patterns are labeled and separated from the current default.
- Device-only behavior is not presented as Simulator-verifiable.
- Examples preserve error handling, cancellation, accessibility, and state ownership where relevant.

### Scripts

- Scripts exist only for repeated or deterministic work.
- Interfaces are non-interactive, provide useful help, fail with actionable errors, and avoid destructive defaults.
- Structured output and exit codes are stable enough for agent use.
- Tests cover meaningful success and failure behavior.

### Evaluations

- Prompts resemble real requests and include near-miss routing cases.
- Assertions verify behavior or evidence rather than exact wording.
- Changed behavior has a regression case.
- Where practical, compare with-skill and without-skill results and record quality, token, and duration tradeoffs.
- Local and published formats remain covered by repository consistency checks.

## Collection checks

Run:

```sh
python3 .github/scripts/validate_repository.py
python3 -m unittest discover -s tests -v
npm ci
npm test
npm run pack:check
claude plugin validate .
python3 .github/scripts/check_sosumi_links.py
python3 .github/scripts/validate_public_discovery.py --run
```

Then inspect:

- exact membership across `skills/`, Claude bundles, and Tessl metadata
- total discovery-description size and high-overlap descriptions
- oversized entrypoints and reference routing
- local and published eval inventory, schema consistency, and orphan cases
- CI coverage, branch protection, version consistency, tags, and releases
- stale repository instructions or missing maintainer tooling

## Release gate

A release is ready only when:

- repository validation and tests pass
- npm, Claude, and Tessl manifests agree on version and skill membership
- installation discovery returns the expected public catalog
- changed skills have relevant eval evidence
- changelog and release notes describe user-visible changes
- required publishing credentials are configured without exposing secrets
- Git status contains only intended release changes

Do not create a tag, GitHub Release, or registry publication without user authorization.

The npm wrapper pins installations to the Git tag matching `package.json`. After the tag release workflow succeeds and npm publication is explicitly authorized, publish and verify from outside the repository:

```sh
npm publish --access public
npm view @thiennc/ios-skills version
npx --yes @thiennc/ios-skills --version
```

## Report

Lead with the conclusion, then classify findings:

- **P0:** invalid packaging, unsafe guidance, broken release path, or widespread routing failure
- **P1:** material accuracy, discovery, eval, or maintenance weakness
- **P2:** useful cleanup or incremental coverage improvement

For each finding include evidence, impact, and the smallest reasonable correction. State what is already healthy. After requested changes, re-run focused validation, repository tests, npm package validation, clean discovery, and GitNexus change detection before commit.
