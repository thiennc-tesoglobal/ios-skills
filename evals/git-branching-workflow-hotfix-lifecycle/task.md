# Production Hotfix Branching and Release Routing

## Problem/Feature Description

An emergency crash on launch occurs in production version `v1.2.0`. A targeted hotfix must be deployed immediately without incorporating features currently in development on `main`.

## Output Specification

Document the git workflow to branch off the exact production release tag, apply the minimal fix, tag the resulting release patch `v1.2.1`, and merge the change back into both the release path and `main` to prevent regression.
