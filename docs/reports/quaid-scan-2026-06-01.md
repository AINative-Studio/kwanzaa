# quaid-scanner Report: /Users/karstenwade/Projects/AINative-Studio/src/kwanzaa

**Score:** 🔴 2.3/10 — CRITICAL risk
**Maturity:** sandbox | **Depth:** standard | **Duration:** 0.1s
**Scanned:** 2026-06-01T21:39:25.650Z

## Pillar Scores

| Pillar | Score | Weight | Findings |
|--------|-------|--------|----------|
| Security | 3.5 | 25% | 0C 4W 1I |
| Governance | 2.0 | 20% | 0C 2W 10I |
| Community | 2.5 | 15% | 0C 2W 9I |
| AI Readiness | 2.5 | 15% | 0C 5W 0I |
| Inclusive Language | 0.0 | 15% | 0C 4W 16I |
| Technical Rigor | 3.0 | 10% | 1C 2W 2I |

## Critical Findings

### test-coverage-1
**Pillar:** Technical Rigor | **Category:** test-coverage

No test files detected in the repository

_(source: local file check)_

**Suggestion:** Add a test suite to improve code reliability and enable coverage tracking

**Reference:** https://chaoss.community/metric-test-coverage/

## Warnings

- **[TIMEOUT-binary-artifacts]** Scanner "binary-artifacts" timed out after undefinedms *(Increase scannerTimeout in configuration or check network connectivity)*
- **[TIMEOUT-dep-pinning-docker]** Scanner "dep-pinning-docker" timed out after undefinedms *(Increase scannerTimeout in configuration or check network connectivity)*
- **[TIMEOUT-openssf-local-checks]** Scanner "openssf-local-checks" timed out after undefinedms *(Increase scannerTimeout in configuration or check network connectivity)*
- **[TIMEOUT-openssf-scorecard]** Scanner "openssf-scorecard" timed out after undefinedms *(Increase scannerTimeout in configuration or check network connectivity)*
- **[governance-classification-1]** Unclear governance model — best guess is "Community" with low confidence (35%) *(Document the governance model explicitly in GOVERNANCE.md for clarity)*
- **[TIMEOUT-license-header-scanner]** Scanner "license-header-scanner" timed out after undefinedms *(Increase scannerTimeout in configuration or check network connectivity)*
- **[contributor-funnel-2]** Conversion rates: casual→regular 0%, regular→core 0% *(Low casual-to-regular conversion suggests contributor onboarding friction)*
- **[support-channels-1]** No SUPPORT.md or .github/SUPPORT.md found *(Add a SUPPORT.md documenting how users can get help)*
- **[agentic-rules-2]** CLAUDE.md lacks recognized structural sections *(Add sections like "Critical Rules", "Project Structure", "Common Tasks" to improve agent guidance.)*
- **[TIMEOUT-ai-repo-detection]** Scanner "ai-repo-detection" timed out after undefinedms *(Increase scannerTimeout in configuration or check network connectivity)*
- **[TIMEOUT-dataset-provenance]** Scanner "dataset-provenance" timed out after undefinedms *(Increase scannerTimeout in configuration or check network connectivity)*
- **[TIMEOUT-model-card-detection]** Scanner "model-card-detection" timed out after undefinedms *(Increase scannerTimeout in configuration or check network connectivity)*
- **[TIMEOUT-model-card-scoring]** Scanner "model-card-scoring" timed out after undefinedms *(Increase scannerTimeout in configuration or check network connectivity)*
- **[TIMEOUT-diminishing-language-scanner]** Scanner "diminishing-language-scanner" timed out after undefinedms *(Increase scannerTimeout in configuration or check network connectivity)*
- **[TIMEOUT-inclusive-code-scanner]** Scanner "inclusive-code-scanner" failed: Cannot read properties of undefined (reading 'termListUrl') *(Check scanner implementation for errors)*
- **[TIMEOUT-inclusive-doc-scanner]** Scanner "inclusive-doc-scanner" failed: Cannot read properties of undefined (reading 'termListUrl') *(Check scanner implementation for errors)*
- **[TIMEOUT-inclusive-naming-scanner]** Scanner "inclusive-naming-scanner" failed: Cannot read properties of undefined (reading 'termListUrl') *(Check scanner implementation for errors)*
- **[interaction-templates-1]** No issue templates configured *(Add .github/ISSUE_TEMPLATE/ with bug report and feature request templates)*
- **[linter-config-1]** No linter configuration found *(Add a linter (ESLint, Prettier, Ruff, golangci-lint, etc.) and configure it to run in CI)*

## Info

- **[branch-protection-1]** GitHub token not provided. Cannot check branch protection settings.
- **[asset-protection-1]** No trademark policy found (optional)
- **[asset-protection-2]** No export control documentation found (optional)
- **[asset-protection-3]** No CLA or DCO requirement detected
- **[asset-protection-4]** Contributor friction level: Low
- **[bus-factor-1]** Bus factor: 1, Elephant factor: 57% (2 contributors, 42 commits in last 12 months)
- **[dep-license-scanning-1]** No dependency manifest files found
- **[governance-detection-1]** No governance documentation found
- **[license-compatibility-1]** Project license is GPL-3.0 — no installed dependencies to check compatibility
- **[vendor-neutrality-domain-count]** Found 2 unique email domain(s) across 42 commits
- **[vendor-neutrality-no-succession]** No succession planning documentation found
- **[burnout-detection-1]** Burnout detection requires a GitHub token
- **[contributor-data-1]** 2 unique contributors with 42 commits in the last 12 months
- **[contributor-data-2]** Contributor emails span 2 domains
- **[contributor-funnel-1]** Contributor funnel: 0 core, 2 regular, 0 casual (2 total)
- **[funding-1]** No funding infrastructure detected
- **[issue-closure-1]** Issue closure analysis requires a GitHub token
- **[response-classification-1]** Response classification requires a GitHub token
- **[response-time-1]** Response time analysis requires a GitHub token
- **[stale-bot-1]** No stale bot configured
- **[AK-GIT-CLONE-README.md:149]** Assumed knowledge: "clone" operation used without explanation
- **[AK-GIT-CLONE-README.md:152]** Assumed knowledge: "clone" operation used without explanation
- **[AK-ACRONYM-RAG-README.md:5]** Undefined acronym "RAG" may confuse newcomers
- **[AK-ACRONYM-AGENTS-README.md:91]** Undefined acronym "AGENTS" may confuse newcomers
- **[AK-ACRONYM-README-README.md:100]** Undefined acronym "README" may confuse newcomers
- **[AK-ACRONYM-CODEOWNERS-README.md:283]** Undefined acronym "CODEOWNERS" may confuse newcomers
- **[AK-GIT-FORK-CONTRIBUTING.md:21]** Assumed knowledge: "fork" operation used without explanation
- **[AK-GIT-CLONE-CONTRIBUTING.md:22]** Assumed knowledge: "clone" operation used without explanation
- **[AK-TOOL-MAKE-CONTRIBUTING.md:24]** Assumed knowledge: "make" command used without build tools listed as prerequisite
- **[AK-TOOL-MAKE-CONTRIBUTING.md:185]** Assumed knowledge: "make" command used without build tools listed as prerequisite
- **[AK-ACRONYM-CSV-CONTRIBUTING.md:91]** Undefined acronym "CSV" may confuse newcomers
- **[AK-ACRONYM-GPL-CONTRIBUTING.md:107]** Undefined acronym "GPL" may confuse newcomers
- **[AK-ACRONYM-ODC-CONTRIBUTING.md:125]** Undefined acronym "ODC" may confuse newcomers
- **[AK-ACRONYM-PEP-CONTRIBUTING.md:144]** Undefined acronym "PEP" may confuse newcomers
- **[AK-ACRONYM-README-CONTRIBUTING.md:164]** Undefined acronym "README" may confuse newcomers
- **[AK-ACRONYM-CONTRIBUTORS-CONTRIBUTING.md:218]** Undefined acronym "CONTRIBUTORS" may confuse newcomers
- **[release-cadence-1]** No releases or version tags found
- **[semver-validation-1]** No git tags found — cannot validate SemVer

## Recommendations

- **[HIGH impact / medium effort]** Add a test suite to improve code reliability and enable coverage tracking
  - https://chaoss.community/metric-test-coverage/
- **[MEDIUM impact / low effort]** Increase scannerTimeout in configuration or check network connectivity
- **[MEDIUM impact / low effort]** Document the governance model explicitly in GOVERNANCE.md for clarity
- **[MEDIUM impact / low effort]** Increase scannerTimeout in configuration or check network connectivity
- **[MEDIUM impact / low effort]** Low casual-to-regular conversion suggests contributor onboarding friction
- **[MEDIUM impact / low effort]** Add a SUPPORT.md documenting how users can get help
- **[MEDIUM impact / low effort]** Add sections like "Critical Rules", "Project Structure", "Common Tasks" to improve agent guidance.
- **[MEDIUM impact / low effort]** Increase scannerTimeout in configuration or check network connectivity
- **[MEDIUM impact / low effort]** Increase scannerTimeout in configuration or check network connectivity
- **[MEDIUM impact / low effort]** Check scanner implementation for errors
- **[MEDIUM impact / low effort]** Add .github/ISSUE_TEMPLATE/ with bug report and feature request templates
- **[MEDIUM impact / low effort]** Add a linter (ESLint, Prettier, Ruff, golangci-lint, etc.) and configure it to run in CI

## Score Rationale

Overall score is a weighted sum of six pillar scores (each scored 0–10).

| Pillar | Weight | Raw Score | Contribution |
|--------|--------|-----------|-------------|
| Security | 25% | 3.5 | 0.88 |
| Governance | 20% | 2.0 | 0.40 |
| Community | 15% | 2.5 | 0.38 |
| AI Readiness | 15% | 2.5 | 0.38 |
| Inclusive Language | 15% | 0.0 | 0.00 |
| Technical Rigor | 10% | 3.0 | 0.30 |
| **Overall** | **100%** | | **2.30** |

---
*quaid-scanner v0.1.2 | 2026-06-01T21:39:25.650Z*
*Commit: 118f69491c3adf5ab626f0229360a6c1a469b7f5*