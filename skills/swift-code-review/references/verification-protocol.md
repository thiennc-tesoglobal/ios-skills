# Review Verification Protocol

> Adapted and rewritten for this collection; see [../NOTICE.md](../NOTICE.md).

Use this protocol before retaining any finding. It is intentionally short enough
to apply to every issue and strict enough to prevent plausible but unverified
claims.

## Gates

1. **Artifact.** Re-read the exact `FILE:LINE` and quote or paraphrase the
   observable code in your notes. For a diff review, inspect the actual diff hunk
   and then the full enclosing symbol.
2. **Context.** Read at least one relevant line outside the changed hunk so that
   control flow, scope, and lifetime are understood.
3. **Usage.** Before “unused,” “dead,” or “never called,” search all targets for
   direct references, imports, `@objc`, `#selector`, key paths, tests, and
   framework callbacks. Record the result.
4. **Upstream responsibility.** Before “missing validation” or “missing error
   handling,” inspect the caller, parent view/model, coordinator, delegate, and
   framework contract. Name the layer that owns the responsibility.
5. **Current API.** Verify availability, isolation, and syntax against current
   Apple/Swift primary documentation when the finding depends on an API detail.
6. **Intent.** Check comments, tests, project instructions, and surrounding
   conventions. Distinguish a deliberate trade-off from an accidental defect.
7. **Severity.** Remove style-only and hypothetical issues. Use the narrowest
   severity supported by observable impact; downgrade uncertainty to a hypothesis
   or Informational note.

## Issue-specific cautions

### Memory and races

- Confirm the owner can actually outlive or retain the operation.
- Check `cancel()`, `deinit`, `onDisappear`, sequence termination, subscription
  disposal, and delegate teardown before claiming cleanup is missing.
- Trace the value across every `await` before claiming actor reentrancy or a race.

### Performance

- Confirm the code runs on a hot path (body/layout/scroll loop) or at a scale
  where the cost matters.
- Treat a code-only performance concern as a hypothesis until Instruments,
  MetricKit, or a reproducible measurement shows impact.
- Do not prescribe an optimization when the framework already provides the
  relevant diffing, lazy loading, or observation behavior.

### Assertions and casts

- Distinguish a type annotation from a forced cast or unwrap.
- Check framework guarantees and prior narrowing before flagging a cast.
- Test and prototype code can have different failure contracts; keep findings in
  scope and label production impact accurately.

## Final pass

Before submitting, ask:

- Can I point to the exact line and explain why it is a defect rather than a
  preference?
- Did I check the caller and all relevant ownership/error paths?
- Would fixing this change correctness, safety, user experience, or measurable
  maintainability?
- Does the proposed fix avoid introducing a new unreviewed abstraction or
  dependency? If net-new infrastructure is only a suggestion, mark it
  Informational.
- Are all findings numbered, severity-labeled, and written as
  `[FILE:LINE] ISSUE_TITLE`?

If a question remains unresolved, state the missing evidence instead of asserting
the issue.
