# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-02-13
### Added
- Regex rule type support for policy rules (e.g., validate `serving_endpoint_name` against a pattern).
- Rule constants for regex validation (`TYPE_REGEX`, `RULE_PATTERN`).

## [0.2.0] - 2026-02-11
### Added
- `changes_made` flag in `PolicyResult` to indicate when corrections modify config.
- AI Gateway updates for `fallback_config` and `usage_tracking_config`.
- Update flow can skip changes when configuration is already up to date.

### Changed
- Enhanced policy evaluation flow to support safer dry runs and update decisions.

## [0.1.0] - 2026-02-04
### Added
- Core policy engine for Databricks serving endpoint configs.
- PolicyManager for loading, validating, and applying policies.
- Rule types `required` and `fixed` with dot‑notation keys.
- Rate‑limit rule parsing for user, user_group, and principal.
- `dry_mode` for safe policy evaluation without applying changes.
- Rule filtering via `get_rules_by_prefix`.
- Endpoint `details` metadata in domain model.
- JSON schema validation for policies and rules.

