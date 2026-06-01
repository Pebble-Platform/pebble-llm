# Verification Report: {{FEATURE_NAME}}

**Sub-feature spec:** `spec/{{feature-slug}}/{{subfeature-slug}}/spec.md`
**Parent feature:** `spec/{{feature-slug}}/spec.md`
**Generated:** {{YYYY-MM-DD HH:MM}} (UTC)
**Commit:** `{{git short SHA}}`
**Tier:** Small / Medium / Large
**Verdict:** PASS / PASS WITH NOTES / FAIL

---

## 1. Trace Matrix

<!-- One row per REQ/NFR/AC from the spec. Every REQ and NFR MUST appear.
     If a row has no concrete Test Location + Command + PASS Result (or
     approved Manual / Log-inspection evidence), verdict is FAIL.

     Column meanings:
     - REQ ID / AC ID    : copied from spec.md (keep IDs stable)
     - Verification Method: Automated test / Manual procedure / Log inspection
     - Test Location     : file:line for automated; doc path for manual
     - Command           : exact invocation used for Result (or "n/a" for manual)
     - Result            : PASS (duration) / FAIL / SKIP / MANUAL-PASS
     - Evidence          : stdout excerpt, log path, screenshot path, or measured value
-->

| REQ ID | AC ID | Verification Method | Test Location | Command | Result | Evidence |
|--------|-------|---------------------|---------------|---------|--------|----------|
| REQ-001 | AC-001 | Automated test | `test/path/file.test.ts:42` | `{{test runner invocation}}` | PASS ({{duration}}) | {{one-line stdout excerpt or log path}} |
| REQ-002 | AC-002-01 | Manual procedure | `docs/manual/{{proc}}.md` | n/a | MANUAL-PASS | {{operator + date + screenshot path}} |
| NFR-001 | — | Log inspection | — | `{{bench/metric command}}` | PASS ({{measured value}} < {{threshold}}) | `{{output-file path}}` |

---

## 2. Test Run Summary

<!-- Counts across the full suite run at this commit. Implementation-supporting
     tests (regression guards, edge-case safety nets) are counted here but NOT
     enumerated in the Trace Matrix. Per the guide: the anti-pattern is
     "no tests trace back to the spec at all", not "tests exist that are not
     in the matrix". -->

- **Suite:** {{framework + version}}
- **Total:** {{N}}   **Passed:** {{N}}   **Failed:** 0   **Skipped:** 0
- **Duration:** {{X}}s
- **Exit code:** 0
- **Coverage (if measured):** {{pct}} ({{tool}})

---

## 3. Deviations

<!-- Classify any mismatch using the taxonomy in
     skills/verification/references/deviations.md:
     GAP / UNTESTED / FAILING / UNSPECIFIED / SPEC DEVIATION.

     Empty section if clean. Any UNTESTED or FAILING row here forces FAIL. -->

| # | Type | REQ/AC | Description | Action Taken |
|---|------|--------|-------------|--------------|
| — | — | — | No deviations. | — |

---

## 4. Reconciliation

<!-- Spec updates driven by accepted SPEC DEVIATIONs above. Format per
     deviations.md "Spec update note format". Leave as "No reconciliation
     needed." if there were no deviations. -->

- **Sub-feature spec.md:** {{list sections touched, or "no updates needed"}}
- **Parent spec.md (Business Context):** {{sections touched, or "no parent updates needed"}}
- **Parent code_context.md:** {{Entry Points / Core Modules / Data Flow / Seams / Known Gotchas / Related Tests — list touched or "no parent updates needed"}}
- **last-reviewed bumps:** {{file list, or "none"}}

---

## 5. Signoff

- [ ] Every REQ and NFR from spec.md has a row in the Trace Matrix above
- [ ] Every matrix row has a concrete Test Location + Command + passing Result (or approved Manual/Log evidence)
- [ ] All tests in the suite pass (see §2); zero FAILING rows in §3
- [ ] No UNTESTED rows remain unreconciled (UNTESTED blocks signoff per deviations.md)
- [ ] Shadow specs promoted or discarded
- [ ] Reconciliation complete (§4)

**Verdict rationale:** {{one sentence — why this verdict was chosen}}

**Verdict line:**

- **PASS:** `Verification complete for spec/{{feature-slug}}/{{subfeature-slug}}/. All REQs verified with evidence. Report: verification-report.md. Parent updated: {{list or 'no parent changes needed'}}.`
- **PASS WITH NOTES:** `Verification complete with notes for spec/{{feature-slug}}/{{subfeature-slug}}/. See §3 for acceptable deviations. Report: verification-report.md. Parent updated: {{list or 'no parent changes needed'}}.`
- **FAIL:** `Verification FAILED for spec/{{feature-slug}}/{{subfeature-slug}}/. {{N}} REQ/AC rows without evidence or with FAILING tests. See §3 for details.`
