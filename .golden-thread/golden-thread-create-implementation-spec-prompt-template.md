Create a decision-complete implementation spec for `{FEATURE_ID}`: `{FEATURE_TITLE}`.

Use the structure and rigor of `.agents/.golden-thread/implementation-specs/FEAT-ING-001/FEAT-ING-001-SPEC.md`.

The spec must be detailed enough that another engineer or agent can implement the feature without making product, architecture, API, error-handling, test, or rollout decisions.

Include these sections:

# {FEATURE_ID} Implementation Spec: {FEATURE_TITLE}

## Status

Include:
- Feature ID
- Title
- Owner
- Release / version
- Implementation order
- Current status
- Source page or tracking reference
- Direct Golden Thread relations

## Overview

Describe:
- What the feature does
- Why it exists
- Which existing route, service, UI, workflow, or system boundary invokes it
- What behavior it replaces or extends
- What downstream features depend on it
- What remains intentionally placeholder or future work

## Golden Thread Trace

Create a table with:

| Layer | ID | Requirement / responsibility | Feature coverage |
| --- | --- | --- | --- |

Cover all relevant layers, such as:
- Business Requirement
- User Requirement
- Functional Requirement
- REST Endpoint
- Call Flow
- Service
- Interface
- Database, RPC, GraphQL, Event, or external integration if applicable
- Test Case
- Verification

Also include an “Out-of-scope Golden Thread layers” list for layers intentionally not covered by this slice.

## Requirements

### Functional

List concrete, testable functional requirements.

Each requirement must state:
- Required behavior
- Inputs or triggers
- Expected output or state change
- Important constraints

### Non-Functional / Operational

Include only relevant production concerns, such as:
- Security
- Privacy / secret handling
- Performance
- Reliability
- Observability
- Configurability
- Failure isolation

### Boundaries

Split into:
- In scope
- Out of scope

Be explicit enough to prevent scope creep during implementation.

## Interfaces And Contracts

Document every public or internal contract touched by the feature.

For each interface, include:
- Name and location
- Request/input shape
- Success response/output shape
- Error response/output shape
- Status codes, exception types, or return states
- Compatibility notes
- Validation rules
- Security redaction rules

Use JSON examples for REST contracts and typed examples for internal service contracts.

## Data Flow

Describe the end-to-end flow as numbered steps.

Include:
- Caller
- Validation
- Service orchestration
- Persistence or filesystem behavior
- External calls
- Error mapping
- Cleanup behavior
- Returned result
- Future consumers

If relevant, include lifecycle policy:
- Creation
- Retention
- Cleanup
- Idempotency
- Retry behavior

## Implementation Changes

Group changes by subsystem, for example:

### Backend

Specify:
- Modules/files to add or update
- New classes/functions/types
- Route or service wiring
- Settings/env vars
- Error handling
- Logging/observability
- Security controls

### Frontend

Specify:
- Components/routes to update
- API client changes
- UI states
- Validation/display behavior

### Database / Infrastructure

Specify:
- Migrations
- Indexes/constraints
- Docker/env changes
- External service configuration

### Manifests And Docs

Specify:
- Golden Thread manifest updates
- Inline `@golden-thread` annotations
- README or operational documentation updates
- `.env.example` changes
- `.gitignore` changes if generated/local artifacts are introduced

## Edge Cases And Failure Modes

Create a table:

| Case | Expected behavior |
| --- | --- |

Include:
- Invalid input
- Unsupported input
- Missing dependencies
- Permission failures
- Timeouts
- Network failures
- Duplicate requests
- Partial writes or cleanup failures
- Secret or raw error leakage risks
- Backward compatibility risks

## Test And Verification Mapping

Create a table:

| Test | Type | Golden Thread IDs | Required assertions |
| --- | --- | --- | --- |

Include:
- Unit tests
- Integration tests
- Contract tests
- Optional live/external tests
- Security regression tests
- Failure-path tests

Then add explicit verification criteria:
- What must pass locally
- What must pass in CI
- Which tests are mocked vs live
- Which checks prove no secrets or raw internal errors leak

## Acceptance Criteria

List final done criteria.

Each item must be objectively verifiable, such as:
- API returns expected status and response
- Required configuration exists
- Safe error mapping works
- Tests pass
- Docker/build commands pass
- Golden Thread traceability is updated
- Docs are updated
- No credentials or generated artifacts are committed

## Commit Plan

Provide a PR-ready commit sequence.

Use a table:

| Commit | Message | Contents | Validation gate |
| --- | --- | --- | --- |

Each commit should:
- Be independently understandable
- Keep related changes together
- Include required Golden Thread IDs in commit body guidance
- Define the validation command/check for that commit

Also include commit rules:
- Files/artifacts not to commit
- Scope exclusions
- Required traceability IDs
- Required validation before pushing

## Source References

List:
- Feature source page
- Related Business/User/Functional requirements
- Related call flows
- Test cases
- Verification records
- Config/manifest references
- External documentation references if needed

## Ready-To-Implement Checklist

Before finalizing the spec, ensure it answers:

- What exact behavior is being built?
- What is explicitly not being built?
- Which public contracts change?
- Which internal contracts change?
- What are the validation rules?
- What are the safe error messages and status codes?
- What configuration is required?
- What data is created, retained, or cleaned up?
- What security/privacy risks are addressed?
- What tests prove the happy path?
- What tests prove failure paths?
- What docs/manifests need updates?
- What commands prove the implementation is complete?
- What commit sequence should be used?