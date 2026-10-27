"""Command-line behavior through the existing environment and runner macros."""

import unittest

from test_littletest import AUTO_MAIN, HeaderHarness, SUITE


REGISTERED_TESTS = '''
#include "littletest.hpp"
LT_BEGIN_SUITE(S)
void set_up() { std::cout << "fixture setup\\n"; }
void tear_down() { std::cout << "fixture cleanup\\n"; }
LT_END_SUITE(S)
LT_BEGIN_TEST(S,Alpha)
std::cout << "body Alpha\\n";
LT_CHECK(true);
LT_END_TEST(Alpha)
LT_BEGIN_TEST(S,AlphaLong)
std::cout << "body AlphaLong\\n";
LT_CHECK(true);
LT_END_TEST(AlphaLong)
LT_BEGIN_TEST(S,Beta)
std::cout << "body Beta\\n";
LT_CHECK(true);
LT_END_TEST(Beta)
'''


class CliTests(HeaderHarness):
    def test_no_arguments_preserve_all_tests(self):
        result = self.compile_and_run(REGISTERED_TESTS + AUTO_MAIN)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("3 tests executed", result.stdout)
        self.assertEqual(result.stdout.count("fixture setup"), 3)

    def test_auto_filter_runs_only_selected_test_before_fixtures_and_counters(self):
        result = self.compile_and_run(REGISTERED_TESTS + AUTO_MAIN,
                                      args=("--filter", "Beta"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Running test (1): Beta", result.stdout)
        self.assertIn("1 tests executed", result.stdout)
        self.assertNotIn("Alpha", result.stdout)
        self.assertEqual(result.stdout.count("fixture setup"), 1)
        self.assertEqual(result.stdout.count("fixture cleanup"), 1)

    def test_wildcards_are_case_sensitive_full_name_globs(self):
        for pattern, names in (("Alpha*", ["Alpha", "AlphaLong"]),
                               ("?eta", ["Beta"]), ("*a*Long", ["AlphaLong"]),
                               ("**?eta*", ["Beta"]), ("*", ["Alpha", "AlphaLong", "Beta"]),
                               ("alpha*", []), ("Alpha?", []), ("[AB]*", [])):
            with self.subTest(pattern=pattern):
                result = self.compile_and_run(REGISTERED_TESTS + AUTO_MAIN,
                                              args=("--filter=" + pattern,))
                self.assertEqual(result.returncode == 0, bool(names),
                                 result.stdout + result.stderr)
                executed = [line.split(": ", 1)[1] for line in result.stdout.splitlines()
                            if line.startswith("Running test (")]
                self.assertEqual(executed, names)

    def test_manual_filter_preserves_explicit_test_selection_and_order(self):
        result = self.compile_and_run(REGISTERED_TESTS + '''
LT_BEGIN_TEST_ENV()
LT_CREATE_RUNNER(S,r);
LT_RUNNER(r)(Beta)(Alpha)();
LT_END_TEST_ENV()
''', args=("--filter", "*a*"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("2 tests executed", result.stdout)
        self.assertNotIn("AlphaLong", result.stdout)
        self.assertLess(result.stdout.index("body Beta"), result.stdout.index("body Alpha"))

    def test_list_returns_before_environment_body_and_fixtures(self):
        for begin, end in (("LT_BEGIN_TEST_ENV()", "LT_END_TEST_ENV()"),
                           ("LT_BEGIN_AUTO_TEST_ENV()", "LT_END_AUTO_TEST_ENV()")):
            with self.subTest(environment=begin):
                result = self.compile_and_run(REGISTERED_TESTS + begin + '''
std::cout << "environment body\\n";
AUTORUN_TESTS()
''' + end, args=("--list",))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(result.stdout.splitlines(), ["Alpha", "AlphaLong", "Beta"])

    def test_list_respects_filter_in_either_option_order(self):
        for args in (("--list", "--filter=Alpha*"),
                     ("--filter", "Alpha*", "--list")):
            with self.subTest(args=args):
                result = self.compile_and_run(REGISTERED_TESTS + AUTO_MAIN, args=args)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(result.stdout.splitlines(), ["Alpha", "AlphaLong"])

    def test_unknown_or_malformed_options_fail_before_environment_body(self):
        for args in (("--unknown",), ("unexpected",), ("--filter",),
                     ("--filter=",), ("--filter", ""), ("--filter", "--list"),
                     ("--list=yes",), ("--filter=Alpha", "--unknown")):
            with self.subTest(args=args):
                result = self.compile_and_run(REGISTERED_TESTS + '''
LT_BEGIN_AUTO_TEST_ENV()
std::cout << "environment body\\n";
AUTORUN_TESTS()
LT_END_AUTO_TEST_ENV()
''', args=args)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertIn("--", result.stderr)

    def test_filter_with_no_execution_matches_fails(self):
        result = self.compile_and_run(REGISTERED_TESTS + '''
LT_BEGIN_TEST_ENV()
LT_CREATE_RUNNER(S,r);
LT_RUNNER(r)(Beta)();
LT_END_TEST_ENV()
''', args=("--filter", "Alpha"))
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("fixture", result.stdout)
        self.assertIn("0 tests executed", result.stdout)
        self.assertIn("Alpha", result.stderr)
        self.assertIn("match", result.stderr.lower())

    def test_explicit_filter_with_no_list_matches_fails(self):
        result = self.compile_and_run(REGISTERED_TESTS + AUTO_MAIN,
                                      args=("--list", "--filter=Missing"))
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn("Missing", result.stderr)

    def test_execution_matches_survive_summary_resets_across_runners(self):
        result = self.compile_and_run(REGISTERED_TESTS + '''
LT_BEGIN_TEST_ENV()
LT_CREATE_RUNNER(S,first);
LT_RUNNER(first)(Alpha)();
LT_RUNNER(first)();
LT_CREATE_RUNNER(S,second);
LT_RUNNER(second)(Beta)();
LT_END_TEST_ENV()
''', args=("--filter=Alpha",))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.count("0 tests executed"), 2)
        self.assertEqual(result.stdout.count("fixture setup"), 1)

    def test_filtered_registration_is_shared_across_translation_units(self):
        first = SUITE + '''
LT_BEGIN_TEST(S,First)
LT_FAIL("must be filtered out");
LT_END_TEST(First)
''' + AUTO_MAIN
        second = SUITE.replace("SUITE(S)", "SUITE(Other)") + '''
LT_BEGIN_TEST(Other,Second)
LT_CHECK(true);
LT_END_TEST(Second)
'''
        result = self.compile_and_run(first, second, args=("--filter=Second",))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("First", result.stdout)
        self.assertIn("1 tests executed", result.stdout)

    def test_filtered_list_is_shared_across_translation_units(self):
        first = SUITE + '''
LT_BEGIN_TEST(S,First)
LT_FAIL("list must not execute tests");
LT_END_TEST(First)
''' + AUTO_MAIN
        second = SUITE.replace("SUITE(S)", "SUITE(Other)") + '''
LT_BEGIN_TEST(Other,Second)
LT_FAIL("list must not execute tests");
LT_END_TEST(Second)
'''
        result = self.compile_and_run(first, second,
                                      args=("--list", "--filter=Second"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["Second"])

    def test_each_environment_resets_filter_and_match_state(self):
        result = self.compile_and_run(REGISTERED_TESTS + '''
#define main first_environment
LT_BEGIN_TEST_ENV()
LT_CREATE_RUNNER(S,r);
LT_RUNNER(r)(Alpha)();
LT_END_TEST_ENV()
#undef main
#define main second_environment
LT_BEGIN_TEST_ENV()
LT_CREATE_RUNNER(S,r);
LT_RUNNER(r)(Beta)();
LT_END_TEST_ENV()
#undef main
int main() {
    char program[] = "tests", option[] = "--filter=Alpha";
    char* filtered[] = {program,option};
    char* plain[] = {program};
    return first_environment(2,filtered) || second_environment(1,plain);
}
''')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("body Alpha", result.stdout)
        self.assertIn("body Beta", result.stdout)

    def test_empty_environment_is_success_without_a_filter(self):
        result = self.compile_and_run('#include "littletest.hpp"\n' + AUTO_MAIN)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
