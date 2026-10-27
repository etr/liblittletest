# Unworked Review Issues

**Run:** 2026-10-27 14:13:17
**Task:** manual-validation
**Total:** 2 (0 critical, 1 major, 1 minor)

## Major

1. [ ] **test-quality-reviewer** | `tests/test_extensions.py:113` | missing-test
   The accepted NEAR contract preserves long-double precision, but all seven NearTests pass when all three conversions in numbers_near are narrowed to double. A bounded mutation probe confirmed this; LT_CHECK_NEAR(1.0L, 1.0L + std::numeric_limits<long double>::epsilon(), 0.0L) correctly fails with the original header but incorrectly passes with that mutant on this platform. Current tests therefore do not protect this explicit arithmetic requirement.
   *Recommendation:* Add a public-macro regression using adjacent representable long-double values at zero tolerance and assert one failure; this distinguishes narrowing on platforms with wider long-double precision and remains valid where long double equals double.

## Minor

2. [ ] **test-quality-reviewer** | `tests/test_cli.py:197` | redundant-test
   This compiles exactly the same empty automatic environment and checks the same successful exit status already covered by test_littletest.py:417, whose assertions additionally verify the zero-test summary and timing averages. It adds a compiler invocation per matrix configuration without additional regression protection.
   *Recommendation:* Remove this duplicate test and retain test_empty_environment_reports_zero_averages as the no-argument empty-environment compatibility regression.
