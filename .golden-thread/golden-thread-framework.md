# Golden Thread Traceability Framework

## Overview

The **Golden Thread Framework** provides end-to-end traceability from business requirements through architecture, implementation, testing, and deployment. This ensures every line of code can be traced back to a business need, and every business requirement can be traced forward to its implementation.

## Why Use Golden Thread Traceability?

### Benefits

✅ **Accountability**: Every code change ties to a business requirement  
✅ **Completeness**: Ensure all requirements are implemented  
✅ **Impact Analysis**: Understand what's affected when requirements change  
✅ **Audit Trail**: Track decisions and their rationale  
✅ **Onboarding**: New developers understand *why* code exists  
✅ **Quality**: Requirements drive testing, ensuring coverage  

### The Problem Without It

❌ Orphaned code with unknown purpose  
❌ Missed requirements discovered late  
❌ Unclear impact of changes  
❌ Difficulty understanding architectural decisions  
❌ Technical debt accumulation  

---

## Getting Started

### Step 1: Duplicate the Notion Template

1. **Access the Template**  
   Visit: [CodingWizard.AI Golden Thread Template](https://codingwizard-ai.notion.site/) 
   - https://codingwizard-ai.notion.site

2. **Duplicate to Your Workspace**  
   - Click "Duplicate" in the top-right corner
   - Select your team's Notion workspace
   - Rename to match your project: `[Project Name] - Golden Thread Matrix`

3. **Set Permissions**  
   - Share with your engineering team
   - Grant edit access to architects and tech leads
   - Grant view access to stakeholders

### Step 2: Understand the Template Structure

The template contains interconnected databases that maintain traceability:

```
Business Requirements (BR-*)
    ↓
User Requirements (UR-*)
    ↓
Features (FEAT-*)
    ↓
Functional Requirements (FR-*)
Technical & System Requirements (TSR-*)
Non-Functional Requirements (NFR-*)
    ↓
Interface Registry (IF-*)
Call Flows (CF-*)
    ↓
REST Endpoints (REST-*)
GraphQL Operations (GQL-*)
gRPC Methods (RPC-*)
Events (EVT-*)
    ↓
Verification Matrix (V-*)
    ↓
Test Cases (TC-*)
    ↓
Evidence Artifacts (EA-*)
```

Each database has **relations** to upstream and downstream items, creating the "golden thread."

---

## Step-by-Step Population Guide

### Phase 1: Start with Business Requirements (Anchor Point)

**Business Requirements** are the foundation. Start here before writing any code.

#### 1.1: Identify Business Needs

Ask stakeholders:
- What business problem are we solving?
- What value does this provide?
- What are the success metrics?
- Who are the users?

#### 1.2: Create Business Requirement Records

**Template Fields:**
- **BR ID**: `BR-[DOMAIN]-[NUMBER]` (e.g., `BR-MON-001` for "Monetization 001")
- **Title**: Clear, business-focused name
- **Description**: What business value this provides
- **Priority**: Critical / High / Medium / Low
- **Stakeholder**: Who requested this
- **Success Metrics**: How we measure success

**Example:**
```
BR-MON-001: Multi-Tenant Account Management
Description: Enable users to create accounts and manage billing 
             to support our SaaS business model
Priority: Critical
Stakeholder: VP of Product
Success Metrics: 
  - 95% successful registration rate
  - < 2 min time to first login
  - Support 10,000 concurrent users
```

**💡 Pro Tip**: Use Notion AI to expand brief notes into full business requirements:
- Write: "need user accounts for saas platform"
- Select text → Ask Notion AI → "Expand this into a business requirement with description, priority, stakeholders, and success metrics"

#### 1.3: Link to Related Documents

Add links to:
- PRD (Product Requirements Document)
- Business case documents
- Stakeholder meeting notes
- Market research

### Phase 2: Derive User Requirements

**User Requirements** describe *what users need to do* to achieve the business requirement.

#### 2.1: Break Down Business Requirements

For each Business Requirement, ask:
- What must users be able to do?
- What workflows are required?
- What user roles are involved?

#### 2.2: Create User Requirement Records

**Template Fields:**
- **UR ID**: `UR-[DOMAIN]-[NUMBER]`
- **Title**: User-focused capability
- **User Story**: As a [role], I want [action], so that [benefit]
- **Acceptance Criteria**: What "done" looks like
- **Business Requirements**: Link to BR records (relation field)

**Example:**
```
UR-MON-001: User Registration
User Story: As a new user, I want to create an account with email 
            and password, so that I can access the platform
Acceptance Criteria:
  - User can enter email and password
  - Email must be unique
  - Password must be at least 8 characters
  - User receives confirmation email
  - User can access dashboard after registration
Business Requirements: [BR-MON-001]
```

**💡 Pro Tip**: Use Notion AI to generate user stories:
- Write business requirement description
- Ask Notion AI → "Generate 5 user stories for this business requirement"
- Review and refine the output

#### 2.3: Add User Personas

Include information about:
- User roles (Admin, User, Guest)
- User expertise level
- Usage patterns
- Edge cases

### Phase 3: Define Features

**Features** are the implementable units that satisfy user requirements.

#### 3.1: Identify Feature Scope

For each User Requirement, determine:
- What system capabilities are needed?
- What components are affected?
- What's the technical scope?

#### 3.2: Create Feature Records

**Template Fields:**
- **FEAT ID**: `FEAT-[COMPONENT]-[NUMBER]`
- **Title**: Technical feature name
- **Description**: What the system will do
- **Components**: Services/modules affected
- **User Requirements**: Link to UR records
- **Status**: Not Started / In Progress / Testing / Complete

**Example:**
```
FEAT-ONBOARD-001: Web App Initial Load with Authentication
Description: Implement user registration, login, session management
Components: Web App, GraphQL Gateway, Account Service, IAM DB
User Requirements: [UR-MON-001], [UR-MON-002]
Status: In Progress
```

**💡 Pro Tip**: Use Notion AI for technical breakdown:
- Paste user requirements
- Ask Notion AI → "Break this into technical features with components and dependencies"

#### 3.3: Add Technical Context

Include:
- Architecture diagrams (paste images or links)
- Technology stack decisions
- Integration points
- Dependencies on other features

### Phase 4: Define Functional, Technical, and Non-Functional Requirements

**Requirements** specify *what* the system must do (FR), *how* it should be built (TSR), and *how well* it should perform (NFR).

#### 4.1: Identify Requirement Types

For each feature, define:
- **Functional Requirements (FR)**: What the system must do
- **Technical & System Requirements (TSR)**: Technical constraints, infrastructure, architecture
- **Non-Functional Requirements (NFR)**: Performance, security, usability, reliability

#### 4.2: Create Functional Requirement Records

**Template Fields:**
- **FR ID**: `FR-[DOMAIN]-[NUMBER]`
- **Title**: Specific functional capability
- **Description**: Detailed functional specification
- **Acceptance Criteria**: How to verify it works
- **Features**: Link to FEAT records
- **Priority**: Must Have / Should Have / Nice to Have

**Example:**
```
FR-AUTH-001: User Registration with Email Validation
Description: System must accept email, display name, and password for registration.
             Email must be validated for format and uniqueness.
             Password must meet complexity requirements.
Acceptance Criteria:
  - Email format validated (RFC 5322)
  - Duplicate email returns specific error
  - Password minimum 8 characters
  - Successful registration creates principal record
  - User receives confirmation (future phase)
Features: [FEAT-ONBOARD-001]
Priority: Must Have
```

**💡 Pro Tip**: Use Notion AI for FR generation:
- Paste feature description
- Ask Notion AI → "Generate functional requirements from this feature with acceptance criteria"

#### 4.3: Create Technical & System Requirement Records

**Template Fields:**
- **TSR ID**: `TSR-[DOMAIN]-[NUMBER]`
- **Title**: Technical constraint or requirement
- **Description**: Technical specification
- **Rationale**: Why this technical approach
- **Features**: Link to FEAT records

**Example:**
```
TSR-DB-001: PostgreSQL Database for IAM
Description: Use PostgreSQL 15+ for IAM database storage
             - ACID compliance required
             - Support for UUID primary keys
             - Full-text search capabilities
             - JSON column support for flexible schemas
Rationale:
  - Proven reliability for user data
  - Strong ACID guarantees
  - Team familiarity
  - Excellent performance for < 1M users
Features: [FEAT-ONBOARD-001]
Alternatives Considered:
  - MongoDB (rejected: need ACID for financial data)
  - MySQL (rejected: weaker JSON support)
```

**💡 Pro Tip**: Use Notion AI for TSR generation:
- Paste feature and architecture context
- Ask Notion AI → "Generate technical and system requirements including infrastructure, security, and performance needs"

#### 4.4: Create Non-Functional Requirement Records

**Template Fields:**
- **NFR ID**: `NFR-[TYPE]-[NUMBER]`
- **Type**: Performance / Security / Usability / Reliability
- **Title**: What quality attribute
- **Description**: Specific measurable requirement
- **Measurement**: How to measure compliance
- **Features**: Link to FEAT records

**Example:**
```
NFR-PERF-001: Authentication Response Time
Type: Performance
Description: User login must complete within 2 seconds under normal load
Measurement:
  - 95th percentile response time < 2s
  - Normal load: 100 concurrent users
  - Measured from request sent to session token received
Features: [FEAT-ONBOARD-001]
Verification: TC-PERF-001, Load testing
```

```
NFR-SEC-001: Password Storage Security
Type: Security
Description: Passwords must be hashed using bcrypt with cost factor >= 12
Measurement:
  - Code review confirms bcrypt usage
  - Cost factor configurable, minimum 12 in production
  - No plaintext passwords in logs or database
Features: [FEAT-ONBOARD-001]
Verification: V-SEC-001, Security audit
```

**💡 Pro Tip**: Common NFR categories:
- **Performance**: Response time, throughput, resource usage
- **Security**: Authentication, authorization, encryption, data protection
- **Usability**: Accessibility, user experience, error messages
- **Reliability**: Uptime, fault tolerance, disaster recovery
- **Scalability**: Horizontal/vertical scaling, load limits
- **Maintainability**: Code quality, documentation, testability

---

### Phase 5: Define Interfaces and APIs

**Interfaces** specify how components communicate. This includes REST APIs, GraphQL operations, gRPC methods, and events.

#### 5.1: Create Interface Records

**Template Fields:**
- **IF ID**: `IF-[DOMAIN]-[NUMBER]`
- **Title**: Interface name
- **Type**: REST / GraphQL / gRPC / Event
- **Description**: What this interface does
- **Requirements**: Link to FR/TSR records
- **Services**: Which services expose/consume

**Example:**
```
IF-API-001: Account Management API
Type: GraphQL + gRPC
Description: Exposes account registration, login, and session management
Requirements: [FR-AUTH-001], [FR-AUTH-002], [TSR-DB-001]
Services:
  - GraphQL Gateway (exposes to frontend)
  - Account Service (implements via gRPC)
Status: Defined
```

#### 5.2: Define REST Endpoints

**Template Fields:**
- **REST ID**: `REST-[DOMAIN]-[NUMBER]`
- **Method**: GET / POST / PUT / DELETE / PATCH
- **Path**: URL path
- **Request**: Request body schema
- **Response**: Response body schema
- **Interface**: Link to IF record

**Example:**
```
REST-AUTH-001: User Registration Endpoint
Method: POST
Path: /api/v1/auth/register
Request:
  {
    "email": "string (required, email format)",
    "displayName": "string (required, 1-100 chars)",
    "password": "string (required, 8+ chars)"
  }
Response (201):
  {
    "userId": "uuid",
    "email": "string",
    "displayName": "string",
    "sessionToken": "string",
    "expiresAt": "ISO8601 timestamp"
  }
Response (400): Validation error
Response (409): Email already exists
Interface: [IF-API-001]
```

#### 5.3: Define GraphQL Operations

**Template Fields:**
- **GQL ID**: `GQL-[TYPE]-[NUMBER]`
- **Operation Type**: Query / Mutation / Subscription
- **Name**: Operation name
- **Schema**: GraphQL schema definition
- **Interface**: Link to IF record

**Example:**
```
GQL-MUT-001: Register User Mutation
Operation Type: Mutation
Name: register
Schema:
  mutation Register($input: RegisterInput!): AuthResponse!
  
  input RegisterInput {
    email: String!
    displayName: String!
    password: String!
  }
  
  type AuthResponse {
    sessionToken: String!
    principal: Principal!
    expiresAt: DateTime!
  }
Interface: [IF-API-001]
```

#### 5.4: Define gRPC Methods

**Template Fields:**
- **RPC ID**: `RPC-[SERVICE]-[NUMBER]`
- **Service**: gRPC service name
- **Method**: Method name
- **Request**: Protobuf request message
- **Response**: Protobuf response message
- **Interface**: Link to IF record

**Example:**
```
RPC-ACCT-001: Register RPC Method
Service: billing.v1.AccountService
Method: Register
Request:
  message RegisterRequest {
    string email = 1;
    string display_name = 2;
    string password = 3;
  }
Response:
  message AuthResponse {
    string session_token = 1;
    Principal principal = 2;
    google.protobuf.Timestamp expires_at = 3;
  }
Interface: [IF-API-001]
Proto File: pkg/proto/billing/v1/account.proto
```

#### 5.5: Define Events

**Template Fields:**
- **EVT ID**: `EVT-[DOMAIN]-[NUMBER]`
- **Event Name**: Name of the event
- **Payload**: Event data schema
- **Producer**: Which service publishes
- **Consumers**: Which services subscribe
- **Features**: Link to FEAT records

**Example:**
```
EVT-USER-001: User Registered Event
Event Name: user.registered.v1
Payload:
  {
    "userId": "uuid",
    "email": "string",
    "displayName": "string",
    "registeredAt": "ISO8601 timestamp"
  }
Producer: Account Service
Consumers: 
  - Email Service (send welcome email)
  - Analytics Service (track conversion)
Features: [FEAT-ONBOARD-001]
```

#### 5.6: Create Call Flows

**Template Fields:**
- **CF ID**: `CF-[FLOW]-[NUMBER]`
- **Title**: Interaction name
- **Actors**: User/systems involved
- **Steps**: Sequence of interactions
- **User Requirements**: Link to UR records

**Example:**
```
CF-LOGIN-001: User Login Flow
Actors:
  - User (Web Browser)
  - GraphQL Gateway
  - Account Service
  - IAM Database
Steps:
  1. User enters email and password in login form
  2. Web App sends GQL-MUT-002 (login mutation) to Gateway
  3. Gateway calls RPC-ACCT-002 (Login RPC) on Account Service
  4. Account Service queries IAM DB for principal by email
  5. Account Service verifies password hash
  6. Account Service creates session in IAM DB
  7. Account Service returns session token to Gateway
  8. Gateway sets HTTP-only cookie with session token
  9. Gateway returns user data to Web App
  10. Web App redirects to dashboard
User Requirements: [UR-MON-002]
Interfaces: [IF-API-001]
Operations: [GQL-MUT-002], [RPC-ACCT-002]
```

**💡 Pro Tip**: Use Notion AI for call flows:
- Paste user requirement
- Ask Notion AI → "Create a call flow diagram description for this user interaction"

---

### Phase 6: Create Test Cases

**Test Cases** ensure requirements are validated.

#### 6.1: Create Test Coverage

For each User Requirement and Functional Requirement, define:
- Unit tests (code-level)
- Integration tests (service-level)
- E2E tests (user-level)
- Performance tests (if NFRs require)
- Security tests (if NFRs require)

#### 6.2: Create Test Case Records

**Template Fields:**
- **TC ID**: `TC-[TYPE]-[NUMBER]`
- **Title**: What is being tested
- **Type**: Unit / Integration / E2E / Performance / Security
- **Test Steps**: How to execute
- **Expected Result**: Pass criteria
- **User Requirements**: Link to UR records
- **Functional Requirements**: Link to FR records
- **Status**: Not Written / Written / Passing / Failing

**Example:**
```
TC-E2E-001: User Registration Flow
Type: E2E
Test Steps:
  1. Navigate to /register
  2. Enter email: test@example.com
  3. Enter display name: Test User
  4. Enter password: SecurePass123!
  5. Submit form
Expected Result:
  - User redirected to /dashboard
  - Welcome message shows "Welcome, Test User"
  - Session persists on page refresh
User Requirements: [UR-MON-001]
Functional Requirements: [FR-AUTH-001]
Status: Passing
```

**💡 Pro Tip**: Use Notion AI for test generation:
- Paste acceptance criteria
- Ask Notion AI → "Generate test cases covering these acceptance criteria with steps and expected results"

#### 6.3: Create Evidence Artifacts

**Template Fields:**
- **EA ID**: `EA-[TYPE]-[NUMBER]`
- **Title**: Evidence description
- **Type**: Test Results / Screenshots / Logs / Reports
- **Test Cases**: Link to TC records
- **Artifacts**: Links to files, screenshots, reports

**Example:**
```
EA-TEST-001: Registration Flow Test Results
Type: Test Results
Description: Playwright E2E test execution results
Test Cases: [TC-E2E-001], [TC-E2E-002]
Artifacts:
  - playwright-report-2025-01-11.html
  - screenshots/registration-success.png
  - test-results.json
Date: 2025-01-11
Status: Passed
```

#### 6.4: Define Verification Methods

**Template Fields:**
- **V ID**: `V-[TYPE]-[NUMBER]`
- **Title**: How to verify requirement
- **Method**: Code Review / Testing / Inspection / Analysis
- **Requirements**: Link to FR/TSR/NFR records
- **Criteria**: What constitutes verification

**Example:**
```
V-SEC-001: Password Hash Verification
Method: Code Review + Security Audit
Requirements: [NFR-SEC-001]
Criteria:
  - Code review confirms bcrypt usage
  - Cost factor >= 12 in production config
  - No plaintext passwords in codebase
  - Security audit passes
Verified By: Security Team
Status: Verified
```

---

### Phase 7: Collect Compliance and Transitional Requirements (Optional)

**Transitional & Compliance Requirements** track regulatory and operational needs.

#### 7.1: Create TCR Records (if applicable)

**Template Fields:**
- **TCR ID**: `TCR-[DOMAIN]-[NUMBER]`
- **Type**: GDPR / HIPAA / SOC2 / Migration / Training
- **Title**: Compliance requirement
- **Description**: What must be complied with
- **Regulation**: Which regulation/standard
- **Features**: Link to FEAT records

**Example:**
```
TCR-GDPR-001: User Data Deletion
Type: GDPR Compliance
Description: System must support complete user data deletion upon request
Regulation: GDPR Article 17 (Right to Erasure)
Requirements:
  - Delete all user personal data
  - Anonymize audit logs (keep IDs only)
  - Complete within 30 days of request
  - Provide deletion confirmation
Features: [FEAT-ONBOARD-001]
Status: Required
```

---

### Phase 8: Organize Services Matrix

**Services Matrix** catalogs all services in the system.

#### 8.1: Create Service Records

**Template Fields:**
- **Service Name**: Descriptive service name
- **Type**: Backend / Frontend / Database / Infrastructure
- **Technology**: Go / TypeScript / Python / PostgreSQL
- **Repository**: Git repository location
- **Features**: Link to FEAT records
- **Interfaces**: Link to IF records exposed/consumed

**Example:**
```
Service Name: account-billing-service
Type: Backend (gRPC Service)
Technology: Go 1.21
Repository: services/account-billing-service/
Features: [FEAT-ONBOARD-001]
Interfaces Exposed: [IF-API-001] via RPC-ACCT-*
Interfaces Consumed: None
Dependencies:
  - PostgreSQL (IAM database)
  - Protocol Buffers
```

---

## Using Notion AI Effectively

### Quick AI Prompts

| Task | Prompt |
|------|--------|
| Expand BR | "Expand this into a business requirement with description, priority, stakeholders, and success metrics" |
| Generate URs | "Generate 5 user stories for this business requirement" |
| Technical breakdown | "Break this into technical features with components and dependencies" |
| Create ADR | "Expand this into an architectural decision record with context, alternatives, and consequences" |
| Task breakdown | "Break this feature into implementation tasks with file paths and estimates" |
| Test generation | "Generate test cases covering these acceptance criteria with steps and expected results" |

### AI Best Practices

✅ **Do**:
- Review and refine AI-generated content
- Add domain-specific context
- Verify technical accuracy
- Customize to your team's standards

❌ **Don't**:
- Blindly accept AI output
- Skip stakeholder validation
- Over-rely on AI for business decisions
- Use AI-generated estimates without review

---

## Maintaining Traceability

### Daily Workflow

1. **Creating New Work**
   - Start in Notion, not in code
   - Trace from BR → UR → FEAT → TASK
   - Link all records before coding

2. **During Implementation**
   - Reference TASK IDs in commit messages: `git commit -m "TASK-ONBOARD-001-03: Implement auth service"`
   - Update task status in Notion
   - Add notes about implementation decisions

3. **During Review**
   - Verify task links to feature
   - Check acceptance criteria are met
   - Update test case status

4. **During Deployment**
   - Create deployment record
   - Link all included features
   - Document rollback plan

### Weekly Maintenance

- **Traceability Audit**: Check for orphaned tasks/features
- **Status Review**: Update all in-progress items
- **Completion Check**: Verify all tasks for deployed features are marked done
- **Metrics Review**: Check requirement completion percentages

### Monthly Reviews

- **Business Alignment**: Review BRs with stakeholders
- **Technical Debt**: Identify items that need revisiting
- **Test Coverage**: Ensure all URs have test cases
- **Documentation**: Update diagrams and specs

---

## Integration with Development Workflow

### Git Commit Messages

Reference traceability IDs:
```bash
git commit -m "FR-AUTH-001, RPC-ACCT-001: Implement user registration logic

Implements bcrypt password hashing and principal creation.
Relates to UR-MON-001 (user registration) and FEAT-ONBOARD-001.
Interfaces: IF-API-001
Tests: TC-INT-001, TC-E2E-001"
```

### Pull Request Templates

Include traceability section:
```markdown
## Traceability
- **Feature**: FEAT-ONBOARD-001
- **Tasks**: TASK-ONBOARD-001-05, TASK-ONBOARD-001-06
- **User Requirements**: UR-MON-002
- **Test Coverage**: TEST-INT-003, TEST-E2E-002

## Changes
- Added session validation middleware
- Updated GraphQL context to include user
- Added integration tests for auth flow
```

### Issue Tracking

Link Notion records in GitHub/Jira:
```
Title: Implement password reset flow
Description: See Notion FEAT-AUTH-002 for full requirements
Labels: FEAT-AUTH-002, UR-MON-003
```

---

## Example: Complete Golden Thread

Here's a full example showing end-to-end traceability:

```
BR-MON-001: Multi-Tenant Account Management
  ↓
UR-MON-001: User Registration
UR-MON-002: User Login
  ↓
FEAT-ONBOARD-001: Web App Initial Load with Authentication
  ↓
FR-AUTH-001: User Registration with Email Validation
FR-AUTH-002: User Login with Credentials
  ↓
TSR-DB-001: PostgreSQL Database for IAM
TSR-GRPC-001: gRPC for Service Communication
  ↓
NFR-PERF-001: Authentication Response Time < 2s
NFR-SEC-001: Bcrypt Password Hashing
  ↓
IF-API-001: Account Management API
  ↓
GQL-MUT-001: Register Mutation
GQL-MUT-002: Login Mutation
RPC-ACCT-001: Register RPC Method
RPC-ACCT-002: Login RPC Method
  ↓
CF-LOGIN-001: User Login Call Flow
  ↓
TC-E2E-001: User Registration E2E Test
TC-E2E-002: User Login E2E Test
TC-INT-001: Account Service Integration Test
TC-PERF-001: Login Performance Test
  ↓
EA-TEST-001: E2E Test Results
V-SEC-001: Password Hash Verification
```

**Traceability Query Examples:**

1. *"What business value does this code provide?"*
   - File: `services/account-billing-service/domain/service/auth_service.go`
   - RPC Method: RPC-ACCT-001
   - Interface: IF-API-001
   - Functional Req: FR-AUTH-001
   - Feature: FEAT-ONBOARD-001
   - User Req: UR-MON-001
   - Business Req: BR-MON-001
   - **Answer**: Enables SaaS business model through account management

2. *"Is UR-MON-002 fully implemented?"*
   - Check: All linked FRs are defined (FR-AUTH-002 ✓)
   - Check: All linked interfaces implemented (IF-API-001 ✓)
   - Check: All linked test cases passing (TC-E2E-002 ✓)
   - Check: Evidence artifacts collected (EA-TEST-001 ✓)
   - **Answer**: Yes, fully verified

3. *"What's the impact of changing password requirements?"*
   - Find: FR-AUTH-001 (user registration)
   - Trace down to: NFR-SEC-001, RPC-ACCT-001, GQL-MUT-001
   - Files: `auth_service.go`, `RegisterForm.tsx`, `account.proto`
   - Tests: TC-E2E-001, TC-INT-001
   - **Answer**: Need to update 3 implementation files, 1 proto, and 2 test cases

4. *"What interfaces does FEAT-ONBOARD-001 expose?"*
   - Find: IF-API-001
   - GraphQL: GQL-MUT-001 (register), GQL-MUT-002 (login)
   - gRPC: RPC-ACCT-001 (Register), RPC-ACCT-002 (Login)
   - **Answer**: 2 GraphQL mutations and 2 gRPC methods

---

## Common Patterns

### Pattern 1: New Feature Request

```
1. Stakeholder requests feature
2. Create BR-[DOMAIN]-[N] with business justification
3. Workshop to derive UR-[DOMAIN]-[N] user stories
4. Technical team creates FEAT-[COMPONENT]-[N]
5. Define FR-[DOMAIN]-[N] functional requirements
6. Define TSR-[DOMAIN]-[N] technical requirements
7. Define NFR-[TYPE]-[N] non-functional requirements
8. Create IF-[DOMAIN]-[N] interface definitions
9. Break down to REST/GQL/RPC endpoints
10. Create TC-[TYPE]-[N] test cases
11. Implement and test
12. Collect EA-[TYPE]-[N] evidence artifacts
13. Verify with V-[TYPE]-[N] methods
14. Mark all records as complete
```

### Pattern 2: Bug Fix

```
1. Bug reported
2. Trace to TC-[TYPE]-[N] (failing test)
3. Find related FR-[DOMAIN]-[N]
4. Determine if acceptance criteria changed
5. If yes: Update FR, create new TC
6. If no: Fix implementation, update TC
7. Collect new EA evidence
```

### Pattern 3: Technical Debt

```
1. Identify technical issue
2. Document in TSR-[DOMAIN]-[N] or NFR-[TYPE]-[N]
3. Link to affected FEAT-[COMPONENT]-[N]
4. Update implementation
5. Ensure tests still pass (TC verification)
6. Update technical documentation
```

### Pattern 4: Adding New Interface

```
1. Start with FR-[DOMAIN]-[N] (what function is needed)
2. Create IF-[DOMAIN]-[N] (interface definition)
3. Define specific endpoints:
   - REST-[DOMAIN]-[N] for REST APIs
   - GQL-[TYPE]-[N] for GraphQL
   - RPC-[SERVICE]-[N] for gRPC
4. Implement interface
5. Create TC-[TYPE]-[N] for interface testing
6. Document in Services Matrix
```

---

## Reporting and Metrics

### Notion Views to Create

1. **Requirements Completion Dashboard**
   - Group by: Business Requirement
   - Show: Linked features, tasks, tests, deployment status
   - Filter: Status != Complete

2. **Sprint Board**
   - Group by: Status (To Do, In Progress, Review, Done)
   - Show: Tasks only
   - Filter: Current sprint

3. **Test Coverage Matrix**
   - Group by: User Requirement
   - Show: All linked test cases
   - Highlight: Missing test coverage

4. **Deployment Timeline**
   - Timeline view of deployment records
   - Group by: Environment
   - Show: Features included in each deployment

### Key Metrics to Track

- **Traceability Coverage**: % of tasks linked to URs
- **Requirement Completion**: % of URs fully implemented
- **Test Coverage**: % of URs with passing tests
- **Orphaned Work**: Tasks not linked to any feature
- **Cycle Time**: Days from BR created to deployed

---

## Team Adoption

### For Product Managers

- **Start with BR**: Define business value first
- **Use AI**: Generate user stories from business needs
- **Track Progress**: Monitor UR completion rates
- **Communicate**: Share Notion views with stakeholders

### For Architects

- **Document Technical Requirements**: Capture architectural decisions
- **Review Features**: Ensure technical feasibility
- **Maintain Diagrams**: Link architecture docs to features
- **Plan Sprints**: Use task breakdown for estimation

### For Developers

- **Reference Tasks**: Check Notion before coding
- **Update Status**: Keep task status current
- **Link Commits**: Reference TASK IDs in commits
- **Add Notes**: Document implementation details

### For QA Engineers

- **Create Tests**: Define test cases from acceptance criteria
- **Track Coverage**: Ensure all URs have tests
- **Report Bugs**: Link bugs to failing tests and URs
- **Update Status**: Mark tests as passing/failing

---

## Troubleshooting

### Common Issues

**Problem**: Too many orphaned tasks  
**Solution**: Enforce linking during task creation, weekly audits

**Problem**: Duplicate requirements  
**Solution**: Search before creating, use consistent naming

**Problem**: Broken links after deletion  
**Solution**: Check relations before deleting, use archive instead

**Problem**: Team not adopting  
**Solution**: Make it easy (templates), show value (metrics), enforce in reviews

**Problem**: Notion getting cluttered  
**Solution**: Archive completed items, use filters, create focused views

---

## Advanced Topics

### Multi-Team Coordination

- Use **prefixes** for domain ownership: `BR-TEAM1-*`, `BR-TEAM2-*`
- Create **cross-team dependency** relation field
- Hold **sync meetings** to review shared features

### API Integration

- Use **Notion API** to sync with Jira/GitHub
- Create **automated status updates** from CI/CD
- Build **custom dashboards** for executives

### Versioning

- Tag features with **release versions**: v1.0, v1.1
- Use **deployment records** to track what's in each version
- Create **changelog views** grouped by version

---

## Resources

### Links

- [Golden Thread Template](https://codingwizard-ai.notion.site/)
- [Notion API Docs](https://developers.notion.com/)
- [ADR Format](https://adr.github.io/)
- [User Story Guidelines](https://www.mountaingoatsoftware.com/agile/user-stories)


### Support

For questions about the Golden Thread Framework:
- **Website**: https://codingwizard.ai
- **Contact**: Araceliz Gomes • aracelizgomes.tech@gmail.com
- **Wiki**: https://codingwizard-ai.notion.site

---

## Quick Start Checklist

- [ ] Duplicate Notion template to your workspace
- [ ] Set up permissions for your team
- [ ] Create your first Business Requirement (BR)
- [ ] Use Notion AI to generate User Requirements (UR)
- [ ] Define your first Feature (FEAT)
- [ ] Document a Technical Design Decision (TDD)
- [ ] Break feature into Tasks (TASK)
- [ ] Create Test Cases (TEST)
- [ ] Plan first Deployment (DEPLOY)
- [ ] Share with team and get feedback
- [ ] Set up weekly traceability reviews
- [ ] Integrate with git commit messages

**Remember**: The golden thread is only valuable if maintained. Make it part of your daily workflow, not an afterthought!

---

