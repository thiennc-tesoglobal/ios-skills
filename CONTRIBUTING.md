# Contributing to iOS Skills

Thank you for helping improve the collection. Contributions should solve a concrete agent behavior problem and remain focused enough to review, test, and maintain.

Use [Issues](https://github.com/thiennc-tesoglobal/ios-skills/issues) for bugs and focused proposals. Use [Discussions](https://github.com/thiennc-tesoglobal/ios-skills/discussions) for broader ideas or roadmap conversations.

## Before you start

- Search existing skills and issues to avoid duplicate work.
- Keep changes scoped to one framework, workflow, or behavior problem.
- Prefer primary Apple, Swift, and Agent Skills documentation for technical claims.
- Preserve the deployment targets and compatibility boundaries stated by the affected skill.
- Avoid unrelated formatting or wording rewrites in the same pull request.

## Skill structure

Every public skill lives in `skills/<skill-name>/` and has a `SKILL.md` file with valid frontmatter.

```text
skills/example-skill/
├── SKILL.md
├── references/   # Optional detailed guidance
├── scripts/      # Optional reusable automation
└── evals/        # Optional local evaluation cases
```

When creating or updating a skill:

1. Give it a lowercase, hyphenated name that matches its folder.
2. Make the description clearly state when the skill should be selected.
3. Define important boundaries and route adjacent work to the correct specialist.
4. Keep `SKILL.md` concise and move conditional detail into directly linked references.
5. Prefer maintainable examples over large copy-paste implementations.
6. Include build, test, runtime, accessibility, or Simulator verification when relevant.
7. Keep every local reference valid and directly discoverable from `SKILL.md`.

Repository-maintainer workflows belong in `.github/maintainer/`, not in `skills/`, so they do not appear as public installable skills.

## Evaluations

Behavior changes should include a new evaluation or update an existing one.

- Local evaluation cases live with the skill and require stable, descriptive names.
- Published scenarios live in `evals/<skill-prefix>-<scenario>/`.
- Each published scenario includes `capability.txt`, `task.md`, and `criteria.json`.
- Criteria should test observable agent behavior rather than specific wording.
- Weighted criteria must total 100.

Cover successful routing, important boundaries, and realistic failure or ambiguity cases where appropriate.

## Local validation

Run the same primary checks used by CI:

```sh
python3 .github/scripts/validate_repository.py
python3 -m unittest discover -s tests -v
npm ci
npm test
npm run pack:check
npx --yes skills@1.5.23 add . --list
```

If Claude marketplace metadata changes, also run:

```sh
claude plugin validate .
```

Resolve validation errors before opening a pull request. Advisory size warnings are opportunities to move detailed material into focused references.

## Pull-request checklist

- [ ] The change addresses one clear problem.
- [ ] Skill names, frontmatter, descriptions, and links are valid.
- [ ] Selection boundaries remain explicit.
- [ ] Technical claims use current primary sources.
- [ ] Relevant evaluation coverage was added or updated.
- [ ] Repository validation and tests pass locally.
- [ ] npm, Claude, and Tessl package metadata remain aligned when changed.
- [ ] The pull request explains what changed and how it was verified.

By contributing, you agree that your contribution is distributed under the repository's [PolyForm Perimeter License 1.0.0](LICENSE).
