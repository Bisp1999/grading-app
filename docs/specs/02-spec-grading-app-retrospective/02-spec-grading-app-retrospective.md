# 02 Spec - Grading App (Retrospective)

## 0. Overview

This document is an after-the-fact specification derived from the current codebase.

**Product name:** Grading App (Multi-tenant)

**Primary users:** Teachers

**Core value:** Allow a teacher to set up their teaching context (teacher type, school(s), classes, subjects/grades, competencies, weightings), manage student rosters, create tests, input grades, and review/adjust grades.

**Non-goal of this spec (for now):** Redesigning the application, changing data model, or committing to compliance requirements. Those will be captured as gaps and follow-up requirements.

## 1. System Context

### 1.1 Tech Stack

- **Backend:** Python + Flask
- **Auth:** Flask-Login (session-based)
- **ORM:** Flask-SQLAlchemy
- **Migrations:** Flask-Migrate / Alembic (partially used; see notes)
- **Localization:** Flask-Babel (English/French)
- **Frontend:** Server-rendered Jinja templates + vanilla JS
- **Styling:** Bootstrap 5

### 1.2 Deployment

- **Local dev:** SQLite (`grading_app.db`) + Flask dev server
- **Production:** Railway + Gunicorn
  - Start command: `gunicorn run:app --bind 0.0.0.0:$PORT` (via `nixpacks.toml`)
  - Also includes a `Procfile`
- **Database:** Production intended to use PostgreSQL via `DATABASE_URL` (Railway)

### 1.3 Configuration

- `FLASK_ENV` selects config (`development` or `production`).
- `SECRET_KEY` is required for sessions and token signing.
- `DATABASE_URL` is used in production config (fallback to SQLite `prod.db` if missing).

## 2. Data Model

### 2.1 Entities (SQLAlchemy Models)

- **Teacher**
  - `first_name`, `last_name`, `email` (unique), `password_hash`, `preferred_language`
- **School**
  - `name`, `teacher_id`
- **Classroom**
  - `name`, `school_id`
- **Student**
  - `first_name`, `last_name`, `classroom_id`
- **SetupWizardData**
  - `teacher_id`
  - `teacher_type`: `homeroom` | `specialist`
  - `school_name`, `num_semesters`
  - JSON text fields: `competencies`, `subjects`, `grades`, `weights`, `classrooms`
  - `grade_name` (homeroom)
  - `subject_name` (specialist)
  - `competencies_skipped` boolean
- **Test**
  - `teacher_id`
  - `semester`
  - Specialist context: `grade`, `class_name`
  - Homeroom context: `subject`
  - `competency`, `test_name`, `max_points`, `test_date`, `test_weight`
  - `scores_modified`, `scores_modified_details` (bell grading tracking)
- **Grade**
  - `test_id`, `student_id`
  - Current values: `grade` (float), `absent` (bool)
  - Original values: `original_grade`, `original_absent`
  - Modification tracking: `modification_type`, `modification_notes`, `modified_at`
  - Unique constraint: `(test_id, student_id)`
- **ClassroomLayout**
  - `teacher_id`, `classroom_id`, `layout_data` (JSON string)

### 2.2 Tenancy / Data Isolation

Isolation is implemented by scoping queries to `current_user.id`:

- Schools: `School.teacher_id == current_user.id`
- Classrooms derived from schools
- Students derived from classrooms
- Tests: `Test.teacher_id == current_user.id`

This is an application-layer tenancy model (no separate schemas).

## 3. User Types and Modes

### 3.1 Teacher Types

Determined primarily from `SetupWizardData.teacher_type`.

- **Homeroom**: single classroom context; grades reviewed primarily by subject.
- **Specialist**: multiple classrooms; creates tests per class and/or per grade.

Some parts of the code also use a heuristic (count of classrooms) as fallback.

### 3.2 Localization

- UI language can be selected (EN/FR)
- Preference stored in `Teacher.preferred_language` when logged in
- Session can store `language`

## 4. Core User Journeys

### 4.1 First-run experience

1. Visit `/`.
2. If not authenticated and no language selected, redirect to `/language_selector`.
3. Register (`/register`) and log in (`/login`).
4. Complete setup wizard (`/setup_wizard`) to define teaching context.
5. Complete student wizard (`/student_wizard`) to populate rosters.
6. Create tests (`/create_tests`).
7. Input grades (`/input_grades`).
8. Review & adjust grades (`/review_grades`).

### 4.2 Setup wizard: Schools + classes

- Implemented as a multi-step UI in `setup_wizard.html` with client-side JS.
- Persists to backend via `POST /setup_wizard/submit`.
- Stores both denormalized JSON (`SetupWizardData`) and normalized entities (`School`, `Classroom`).

Key collected data:

- Teacher type (homeroom/specialist)
- School name, number of semesters
- Competencies list
- Homeroom: subjects list + grade name
- Specialist: grades list + classes per grade + subject name
- Optional competency weighting associations; can be skipped (`competencies_skipped`).

### 4.3 Student wizard: student roster

- `/student_wizard` is a multi-step UI.
- Specialist flow includes:
  - Selecting a class
  - Manual entry of first/last name OR CSV upload
  - Saves via `POST /api/save_students`
- Uses:
  - `GET /api/get_teacher_classrooms`
  - `GET /api/get_classroom_students/<id>`

Notes:

- Homeroom-specific Step 2 notes “coming soon” in template (implementation incomplete).

### 4.4 Create tests

- `/create_tests` shows existing tests and provides a form to create/update/delete.
- Uses global header filters for class + semester.

**New behavior (specialist):** Test scope

- Dropdown `test_scope`:
  - `class_only`: create one test for the selected class
  - `grade_all` (default): create a test for each class in the grade

Editing existing tests forces scope to class-only.

Delete is a single-test delete via `DELETE /api/delete_test/<id>`.

### 4.5 Input grades

- `/input_grades` lets a teacher select a test and enter grades for students.
- UI behavior:
  - Grade input boxes
  - Mark absent toggle
  - Save all grades via `POST /api/save_grades/<test_id>`
  - Enter key moves focus to next grade input.

### 4.6 Review & adjust grades

- `/review_grades` shows a “grade matrix” and actions:
  - Bell grade a test (generate scenarios and apply)
  - Change test weighting
  - Deal with absences
  - Revise grades
  - Export CSV

Data loaded via `GET /api/get_grade_matrix` with filters.

### 4.7 Classroom seating chart

- `/classroom` displays a drag-and-drop seating chart.
- Loads students for selected class and persists layout via:
  - `POST /api/save_classroom_layout`
  - `GET /api/get_classroom_layout/<classroom_id>`

### 4.8 Student tab (student profile)

- `/student_tab` lets teacher select a student (based on selected class) and view:
  - grade history
  - computed stats (low grades threshold)
  - avatar placeholders

Uses `GET /api/get_student_data/<student_id>`.

## 5. Routes & APIs (Inventory)

### 5.1 Auth / Account

- `GET/POST /register`
- `GET/POST /login`
- `GET /logout`
- `GET/POST /forgot_password`
- `GET/POST /reset_password/<token>`

### 5.2 Setup

- `GET /setup_wizard`
- `POST /setup_wizard/submit`
- `GET /api/get_setup_wizard_data`

### 5.3 Students

- `GET /student_wizard`
- `GET /student_tab`
- `GET /api/get_teacher_classrooms`
- `GET /api/get_classroom_students/<classroom_id>`
- `POST /api/save_students`
- `GET /api/get_student_data/<student_id>`

### 5.4 Tests & Grades

- `GET/POST /create_tests`
- `GET/POST /input_grades`
- `GET /review_grades`
- `GET /api/get_tests_for_context`
- `GET /api/get_test/<test_id>`
- `DELETE /api/delete_test/<test_id>`
- `GET /api/get_test_for_grading/<test_id>`
- `POST /api/save_grades/<test_id>`
- `GET /api/get_grade_matrix`
- `POST /api/save_grade_updates`

### 5.5 Bell grading

- `POST /api/bell_grade_scenarios`
- `POST /api/apply_bell_selection`

### 5.6 Classroom seating layout

- `GET /classroom`
- `POST /api/save_classroom_layout`
- `GET /api/get_classroom_layout/<classroom_id>`

### 5.7 Misc

- `GET /set_language/<language>`
- `GET /toggle_language`
- `POST /flush_database` (dangerous; intended for testing)

## 6. Business Rules (Observed)

- Test grading status:
  - A student considered “graded” if `grade.grade is not None` OR `grade.absent == True`.
- Absent students:
  - Input grades page disables grade input when absent.
- Grade tracking:
  - On first create, `original_grade/original_absent` are set equal to current values.
  - Later modifications update current values while preserving original baseline.
- Specialist class matching:
  - In several places, classroom name is stored as `"{class} ({grade})"`.
  - Test stores `class_name` separate from `grade`, requiring matching logic.

## 7. Known Gaps / Risks (Observed)

This section intentionally lists gaps seen in the existing implementation.

### 7.1 Security

- CSRF is likely enabled via Flask-WTF for some forms, but API endpoints using JSON may not be protected.
- `flush_database` endpoint exists behind login; still high-risk if exposed.
- No explicit rate limiting on auth endpoints.
- Password policy minimal (length >= 6 in reset flow).
- No MFA.

### 7.2 Data integrity & migrations

- Some schema changes appear to be applied via one-off scripts (e.g. grade modification columns) rather than Alembic migrations.
- Risk of production schema drift.

### 7.3 Privacy

- Student data includes names; no explicit privacy policy or data retention policy.
- Student photos are placeholders from a third-party avatar API.

### 7.4 Auditability

- Grade changes have some tracking fields but no full audit log (who/when/why) beyond `modified_at` and freeform notes.

### 7.5 Homeroom student wizard

- Template indicates some homeroom flows are incomplete.

## 8. Proof Artifacts (for this retrospective spec)

- Screenshot: Dashboard after setup
- Screenshot: Create Tests form (shows test scope dropdown for specialist)
- Screenshot: Input Grades table with grade entry
- Screenshot: Review Grades matrix loaded for a class+semester
- Screenshot: Classroom seating chart saved state

## 9. Open Questions / Next Requirements (for you to decide)

1. Should multi-tenancy be enforced at the DB level (row-level security) or remain app-layer only?
2. What security baseline is required (CSRF for APIs, rate limiting, password complexity, session expiration rules)?
3. Do we need admin roles?
4. Should teacher be able to export / delete all their data (GDPR-like controls)?
5. Do we need test templates / bulk operations for tests beyond grade-wide creation?

## 10. Security Requirements

### 10.1 High priority

- **Tenant isolation (authoritative rule)**
  - Every read/write of tenant-owned data must be scoped by `current_user.id` (or a derived tenant identifier) in the database query.
  - Avoid patterns that fetch by primary key alone and then check ownership after.
- **CSRF protection for all state-changing requests**
  - All state-changing endpoints (`POST`, `PUT`, `PATCH`, `DELETE`) must have CSRF protection, including JSON `fetch()` APIs.
  - Standardize one approach across HTML forms and JSON APIs.
- **Secure session cookies + session hardening**
  - Enforce secure cookie settings in production: `Secure`, `HttpOnly`, and `SameSite`.
  - Define session lifetime and refresh behavior.
  - Rotate session identifiers on login.
- **Password reset security + correctness**
  - Password reset must work in localhost/dev and in production.
  - Tokens must expire and must not be re-usable (single-use tokens or equivalent invalidation strategy).
  - Production must use a real email delivery configuration; dev may use a safe fallback.
- **Rate limiting & abuse prevention**
  - Add rate limiting for login/registration/password reset endpoints.
  - Add throttling for expensive endpoints (grade matrix, bell grading generation).
- **Security headers baseline**
  - Add a baseline `Content-Security-Policy`.
  - Add clickjacking and MIME-sniffing protections and other standard headers.
- **Production secrets & environment safety**
  - Production must fail fast if `SECRET_KEY` is missing or set to an insecure default.
  - Avoid logging secrets (including password reset tokens).
- **Remove or harden dangerous endpoints**
  - Testing-only destructive endpoints (e.g. `/flush_database`) must be disabled in production, or gated behind explicit admin authorization + re-auth.
- **Authorization checks for all object-level APIs**
  - All endpoints must verify object ownership by the current tenant (tests, classrooms, students, grades, layouts).
  - Prefer returning `404` rather than leaking whether an ID exists for another tenant.

### 10.2 Regular priority

- **Audit logging**
  - Log authentication events and security-relevant actions (grade modifications, exports, password reset completions).
  - Define retention and access policy for logs.
- **Stronger password policy**
  - Increase minimum length, consider blocking common passwords.
- **Optional 2FA / MFA**
  - Consider adding MFA for accounts, particularly in production environments.
- **Data protection requirements**
  - Define retention, export, and deletion behavior for teacher and student data.
- **Dependency & vulnerability management**
  - Define a policy for dependency pinning and vulnerability scanning.
- **Encryption of backup artifacts**
  - Encrypt backups at rest, restrict access, and document recovery procedures.
- **Input validation standards**
  - Define limits and validation rules for user-supplied strings and CSV uploads.
  - Ensure templates never render raw HTML from user input.

### 10.3 Security requirements: user stories, requirements, and acceptance criteria

#### 10.3.1 User stories (security)

- As a teacher, I want my data to be isolated from other teachers so that no one else can view or modify my schools, classes, students, tests, or grades.
- As an operator, I want production defaults (cookies, headers, secrets) to be secure so that the app is safe to run on the public internet.
- As a teacher, I want safe password reset so that I can regain access without compromising account security.

#### 10.3.2 Functional requirements (security)

- **SR-HP-1 Tenant isolation**
  - All CRUD operations on tenant-owned models must be scoped to the current tenant at the query layer.
  - Any endpoint that accepts an object identifier must verify ownership before returning or mutating the object.
- **SR-HP-2 CSRF protection**
  - All state-changing requests must validate CSRF.
  - JSON endpoints must use a consistent CSRF mechanism that works with `fetch()`.
- **SR-HP-3 Session hardening**
  - Production must enforce secure cookie settings.
  - Session lifetime must be defined and enforced.
- **SR-HP-4 Password reset correctness + security**
  - Reset flow must work in dev and production.
  - Tokens must expire and must not be re-usable.
  - Password reset request must not reveal whether an email exists.
- **SR-HP-5 Rate limiting**
  - Add rate limiting for auth and password reset endpoints.
  - Add rate limiting/throttling for expensive endpoints.
- **SR-HP-6 Security headers**
  - Add baseline security headers including a CSP.
- **SR-HP-7 Secrets + environment safety**
  - Production must not run with a default/insecure `SECRET_KEY`.
- **SR-HP-8 Dangerous endpoints**
  - Destructive testing endpoints must not be available in production.

#### 10.3.3 Non-goals / edge cases (security)

- Not implementing full enterprise SSO (SAML/OIDC) in the initial hardening pass.
- Not implementing full “admin console” functionality unless required; focus is on tenant isolation and safe defaults.
- Edge case: a teacher with multiple browser sessions/devices should remain secure (session lifetime, logout behavior).

#### 10.3.4 Implementation notes (aligned to current codebase)

- Centralize tenant-scoped query patterns in helpers (to reduce the chance of missing `teacher_id` filters).
- Prefer join-based ownership verification (e.g., `Student -> Classroom -> School -> teacher_id`) as already used in some endpoints.
- Standardize teacher type derivation using `SetupWizardData.teacher_type` (avoid heuristic mismatches).
- Consider introducing an `is_production` guard and disabling `/flush_database` unless in development.
- Implement CSRF for JSON endpoints using a consistent pattern (e.g., token in a header validated server-side).
- Password reset email delivery is currently implemented via SMTP in `app/routes.py` (`_send_reset_email`) and expects `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_USE_TLS`, `MAIL_USE_SSL` to be configured via environment variables.
- If those variables are not set, the app currently flashes the reset link as a fallback; this is suitable for localhost/dev but not production.
- Production reset URLs are generated with `url_for(..., _external=True)`; in hosted environments this may require proxy/header correctness so generated links use the correct scheme and host.

#### 10.3.5 Acceptance criteria / proof artifacts (security)

- **Tenant isolation**
  - Proof: automated test (or scripted reproduction steps) showing teacher A cannot access teacher B’s resources (tests, students, classrooms, layouts) by ID.
- **CSRF**
  - Proof: a request without CSRF to a state-changing endpoint is rejected; request with CSRF succeeds.
- **Session hardening**
  - Proof: browser devtools shows cookies include `HttpOnly` and (in production) `Secure` and `SameSite`.
- **Password reset**
  - Proof (dev): requesting a reset shows a safe link (or logs a link) and reset succeeds.
  - Proof (prod): requesting a reset sends an email and reset succeeds; token expires after TTL.
  - Proof: token cannot be used twice.
- **Rate limiting**
  - Proof: repeated failed logins and repeated reset requests are throttled.
- **Security headers**
  - Proof: response headers include CSP and other baseline headers.
- **Dangerous endpoints**
  - Proof: `/flush_database` is unavailable or denied in production.

## 11. Backlog / TODOs (Future Features)

### 11.1 Operations

- **DB backups**
  - Provide a teacher-safe and operator-safe backup strategy.
  - Must work in local/dev (SQLite) and production (Railway Postgres).
  - Operational requirement: run backups daily with a retention period of 30 days.
  - Acceptance criteria / proof artifacts:
    - A backup can be triggered and produces an artifact that can be restored into a fresh environment.
    - Production backup artifacts are access-controlled and encrypted.
- **Monitoring / uptime alerting**
  - Monitor the public web service and notify when the service is down.
  - Notification requirement: email notifications only.
  - Acceptance criteria / proof artifacts:
    - An uptime check exists and alerts within a defined window when the app is unreachable.
    - Alerts go to a defined channel (email) and include a link to the failing check.
- **Static asset cache busting (querystring versioning)**
  - Ensure users consistently receive the latest frontend changes after a deploy.
  - Define and use a single `static_version` value (e.g. commit SHA or build ID) that changes every deploy.
  - Append `?v={{ static_version }}` to all local `url_for('static', filename=...)` references (CSS/JS/images) and ensure HTML pages are not aggressively cached.
  - Acceptance criteria / proof artifacts:
    - After deploying a change to a static asset, a browser refresh results in a network request for the new versioned URL (e.g. `app.css?v=<new>`).
    - A user can reliably pick up new UI changes without manual cache clearing.

### 11.2 Authentication

- **Password reset reliability**
  - Ensure reset flow works in localhost/dev and production.
  - Production requires a real email delivery configuration; dev can use a safe fallback.
  - Current implementation note: email delivery is SMTP-based and requires `MAIL_*` environment variables (see `env.example` and `_send_reset_email`).
  - Provider recommendation (low cost / Railway friendly): use an SMTP provider such as **Mailjet** (has a free tier suitable for low-volume transactional email) and set Railway environment variables to its SMTP host/port/credentials.
  - Acceptance criteria / proof artifacts:
    - Dev: request reset and complete reset successfully.
    - Prod: request reset and receive email; complete reset successfully.
    - Token expires after TTL and cannot be re-used.

### 11.3 Student Wizard UX

- **Student Setup Wizard flow order**
  - Update flow so the user selects Class/Grade first, then chooses how to populate names (manual vs upload).
  - Acceptance criteria / proof artifacts:
    - User can select a class first.
    - After selecting a class, user chooses manual or upload and the chosen class context is preserved through save.

### 11.4 Review Grades Feature Completion

- **Bell Grade a Test**
  - Complete and verify scenario generation + apply flow.
  - Validate that modification tracking fields are set appropriately.
  - Acceptance criteria / proof artifacts:
    - For a selected test, scenarios are generated and previewed.
    - Applying a scenario updates grades consistently and sets modification tracking fields.
- **Change Test Weighting**
  - Implement UI + persistence for test weighting updates and ensure grade calculations remain consistent.
  - Acceptance criteria / proof artifacts:
    - Updating a test’s weight persists and is reflected in grade matrix totals.
- **Deal with Absences**
  - Provide tools to manage absences and make-up workflows.
  - Ensure changes are tracked and displayed clearly.
  - Acceptance criteria / proof artifacts:
    - Teacher can mark/unmark absence and the grade matrix and makeup list reflect the change.
- **Revise Grades**
  - Implement manual revision workflow with audit trail via `modification_type`, `modification_notes`, `modified_at`.
  - Acceptance criteria / proof artifacts:
    - Teacher can revise an individual student grade with notes.
    - Original values remain unchanged; modification metadata is saved.
- **Export CSV**
  - Define export formats and filters and implement the download flow.
  - Acceptance criteria / proof artifacts:
    - Export matches selected filters (semester/class/subject as applicable).
    - CSV contains a documented set of columns and downloads successfully.

### 11.5 School Year Lifecycle

- **Archive a school year**
  - Teachers need to archive/roll over from one school year to the next.
  - Decision: archiving makes a school year read-only.
  - Decision: multiple school years must be selectable (teacher can view prior years).
  - Acceptance criteria / proof artifacts:
    - Teacher can archive a year and archived data becomes read-only (or otherwise clearly separated).
    - Teacher can start a new year without losing prior year history.

### 11.6 Student Profile Reporting

- **Semester overview**
  - Add a one-page summary view explaining a student’s final/overall grade and the evidence behind it.
  - Define the outputs (printable page, PDF, or on-screen summary) and what calculations are included.
  - Acceptance criteria / proof artifacts:
    - A single “semester overview” view can be generated for a selected student and semester.
    - Output is printable and includes the calculation breakdown (tests/weights/competencies).

---

*This spec is a first draft based on code inspection and will evolve as we add explicit functional + non-functional requirements.*
