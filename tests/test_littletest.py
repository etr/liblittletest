"""Compile and exercise the distributed header; only Python's standard library is used."""

import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest


HEADER_DIR = Path(__file__).resolve().parents[1] / "src"
SUITE = '''
#include <stdexcept>
#include "littletest.hpp"
LT_BEGIN_SUITE(S)
void set_up() {}
void tear_down() {}
LT_END_SUITE(S)
'''
AUTO_MAIN = '''
LT_BEGIN_AUTO_TEST_ENV()
    AUTORUN_TESTS()
LT_END_AUTO_TEST_ENV()
'''


class HeaderTests(unittest.TestCase):
    def compile_and_run(self, *sources):
        with tempfile.TemporaryDirectory(prefix="littletest-") as directory:
            directory = Path(directory)
            paths = []
            for index, source in enumerate(sources):
                path = directory / ("test%d.cpp" % index)
                path.write_text(source)
                paths.append(str(path))
            executable = directory / ("tests.exe" if os.name == "nt" else "tests")
            command = (shlex.split(os.environ.get("CXX", "c++"))
                       + ["-std=c++11", "-Wall", "-Wextra", "-pedantic"]
                       + shlex.split(os.environ.get("CXXFLAGS", ""))
                       + ["-I", str(HEADER_DIR)] + paths
                       + ["-o", str(executable)])
            compiled = subprocess.run(command, capture_output=True, text=True, timeout=60)
            self.assertEqual(compiled.returncode, 0, compiled.stdout + compiled.stderr)
            result = subprocess.run([str(executable)], capture_output=True,
                                    text=True, timeout=10)
            self.assertNotIn("Sanitizer", result.stderr, result.stderr)
            self.assertNotIn("runtime error:", result.stderr, result.stderr)
            return result

    def run_test_body(self, body, main=AUTO_MAIN, includes=""):
        return self.compile_and_run(includes + SUITE + "LT_BEGIN_TEST(S,T)\n"
                                    + body + "\nLT_END_TEST(T)\n" + main)

    def test_registry_is_shared_across_translation_units(self):
        first = SUITE + '''
LT_BEGIN_AUTO_TEST(S,First)
LT_CHECK(true);
LT_END_AUTO_TEST(First)
''' + AUTO_MAIN
        second = SUITE.replace("SUITE(S)", "SUITE(Other)") + '''
LT_BEGIN_AUTO_TEST(Other,Second)
LT_CHECK(true);
LT_END_AUTO_TEST(Second)
'''
        result = self.compile_and_run(first, second)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("2 tests executed", result.stdout)
        self.assertIn("-> 2 successes", result.stdout)

    def test_manual_environment_preserves_failure_after_summary(self):
        result = self.run_test_body("LT_CHECK(false);", main='''
LT_BEGIN_TEST_ENV()
LT_CREATE_RUNNER(S,r);
LT_RUNNER(r)(T)();
LT_END_TEST_ENV()
''')
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_automatic_failure_status_does_not_wrap_at_256(self):
        result = self.run_test_body("for (int i=0; i<256; ++i) { LT_CHECK(false); }")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("-> 256 failures", result.stdout)

    def test_failed_comparison_evaluates_each_operand_once(self):
        result = self.run_test_body('''
int left = 0, right = 10;
LT_CHECK_EQ(++left, ++right);
std::cout << "evaluations: " << left << "," << right << std::endl;
''')
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("evaluations: 1,11", result.stdout)
        self.assertIn("1 == 11", result.stdout)

    def test_nan_fails_all_ordered_comparisons(self):
        result = self.run_test_body('''
const double n = std::numeric_limits<double>::quiet_NaN();
LT_CHECK_GT(n,0.0);
LT_CHECK_GTE(n,0.0);
LT_CHECK_LT(n,0.0);
LT_CHECK_LTE(n,0.0);
''', includes="#include <limits>\n")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("-> 4 failures", result.stdout)

    def test_comparison_uses_requested_operator(self):
        result = self.run_test_body('''
EqualOnly a, b;
LT_CHECK_EQ(a,b);
''', includes='''
#include <ostream>
struct EqualOnly {};
bool operator==(const EqualOnly&, const EqualOnly&) { return true; }
std::ostream& operator<<(std::ostream& s, const EqualOnly&) { return s << "value"; }
''')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_assertion_macros_are_single_statements(self):
        result = self.run_test_body('''
if (true) LT_CHECK(true); else LT_FAIL("wrong branch");
if (true) LT_CHECK_EQ(1,1); else LT_FAIL("wrong branch");
if (true) LT_CHECK_THROW(throw 1); else LT_FAIL("wrong branch");
if (true) LT_CHECK_NOTHROW(1+1); else LT_FAIL("wrong branch");
if (false) LT_FAIL("wrong branch");
std::cout << "reached end" << std::endl;
''')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("reached end", result.stdout)

    def test_failed_setup_skips_body_but_attempts_cleanup(self):
        result = self.compile_and_run('''
#include "littletest.hpp"
#include <stdexcept>
LT_BEGIN_SUITE(S)
void set_up() { throw std::runtime_error("setup failed"); }
void tear_down() { std::cout << "cleanup attempted" << std::endl; }
LT_END_SUITE(S)
LT_BEGIN_TEST(S,T)
std::cout << "body executed" << std::endl;
LT_END_TEST(T)
''' + AUTO_MAIN)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("body executed", result.stdout)
        self.assertIn("cleanup attempted", result.stdout)
        self.assertIn("-> 1 failures", result.stdout)

    def test_suite_hooks_are_optional(self):
        result = self.compile_and_run('''
#include "littletest.hpp"
LT_BEGIN_SUITE(S)
LT_END_SUITE(S)
LT_BEGIN_TEST(S,T)
LT_CHECK(true);
LT_END_TEST(T)
''' + AUTO_MAIN)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_checkpoint_is_local_to_current_test(self):
        result = self.compile_and_run(SUITE + '''
LT_BEGIN_TEST(S,First)
LT_CHECKPOINT();
LT_END_TEST(First)
LT_BEGIN_TEST(S,Second)
throw std::runtime_error("second test failed");
LT_END_TEST(Second)
''' + AUTO_MAIN)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("Last checkpoint", result.stdout)

    def test_bounded_collections_reject_different_lengths(self):
        result = self.run_test_body('''
int short_range[] = {1};
int long_range[] = {1,2};
LT_CHECK_COLLECTIONS_EQ(short_range,short_range+1,long_range,long_range+2);
LT_CHECK_COLLECTIONS_EQ(long_range,long_range+2,short_range,short_range+1);
LT_CHECK_COLLECTIONS_NEQ(short_range,short_range+1,long_range,long_range+2);
LT_CHECK_COLLECTIONS_NEQ(long_range,long_range+2,short_range,short_range+1);
''')
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("-> 2 failures", result.stdout)
        self.assertIn("-> 2 successes", result.stdout)

    def test_bounded_collections_accept_empty_and_equal_ranges(self):
        result = self.run_test_body('''
int a[] = {1,2};
int b[] = {1,2};
if (true) LT_CHECK_COLLECTIONS_EQ(a,a+2,b,b+2); else LT_FAIL("wrong branch");
LT_ASSERT_COLLECTIONS_EQ(a,a,b,b);
LT_WARN_COLLECTIONS_NEQ(a,a+1,b,b+2);
LT_CHECK_COLLECTIONS_NEQ(a,a,b,b+1);
LT_CHECK_COLLECTIONS_NEQ(a,a+1,b,b);
''')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_bounded_collections_support_single_pass_iterators(self):
        result = self.run_test_body('''
std::istringstream first("1 2 3"), second("1 2 3");
LT_CHECK_COLLECTIONS_EQ(std::istream_iterator<int>(first),std::istream_iterator<int>(),
                        std::istream_iterator<int>(second),std::istream_iterator<int>());
''', includes="#include <iterator>\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_header_does_not_define_generic_severity_macros(self):
        result = self.compile_and_run('''
#define WARN 41
#define CHECK 42
#define ASSERT 43
#include "littletest.hpp"
static_assert(WARN == 41 && CHECK == 42 && ASSERT == 43, "macro collision");
int main() { return 0; }
''')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_timing_averages_use_completed_test_count(self):
        result = self.compile_and_run('''
#include "littletest.hpp"
struct TimedTest {
    const char* lt_name_ = "fixed timing";
    void run_test(littletest::test_runner* runner) {
        runner->add_set_up_time(12.0);
        runner->add_tear_down_time(24.0);
    }
};
int main() {
    TimedTest test;
    littletest::test_runner runner;
    runner(test)(test);
    return runner();
}
''')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Average set up time: 12 ms", result.stdout)
        self.assertIn("Average tear down time: 24 ms", result.stdout)

    def test_duration_uses_monotonic_clock_in_milliseconds(self):
        result = self.compile_and_run('''
#include "littletest.hpp"
int main() {
    static_assert(littletest::clock::is_steady, "timing must be monotonic");
    littletest::clock::time_point start;
    auto end = start + std::chrono::microseconds(1250);
    return littletest::calculate_duration(start,end) == 1.25 ? 0 : 1;
}
''')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_warning_does_not_change_check_counts_or_exit_status(self):
        result = self.run_test_body('''
LT_WARN(false);
LT_WARN_EQ(1,2);
LT_WARN_THROW(0);
LT_WARN_NOTHROW(throw 7);
LT_WARN(true);
LT_CHECK(true);
''')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("-> 1 successes", result.stdout)
        self.assertIn("-> 0 failures", result.stdout)
        self.assertEqual(result.stdout.count("[WARN]"), 4)

    def test_check_failure_continues_test_body(self):
        result = self.run_test_body('''
LT_CHECK(false);
LT_CHECK_EQ(1,2);
LT_CHECK(true);
''')
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("-> 2 failures", result.stdout)
        self.assertIn("-> 1 successes", result.stdout)

    def test_assert_failure_cleans_up_and_continues_next_test(self):
        result = self.compile_and_run('''
#include "littletest.hpp"
LT_BEGIN_SUITE(S)
void tear_down() { std::cout << "cleaned up" << std::endl; }
LT_END_SUITE(S)
LT_BEGIN_TEST(S,First)
LT_ASSERT_EQ(1,2);
std::cout << "unreachable" << std::endl;
LT_END_TEST(First)
LT_BEGIN_TEST(S,Second)
LT_CHECK(true);
LT_END_TEST(Second)
''' + AUTO_MAIN)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("unreachable", result.stdout)
        self.assertEqual(result.stdout.count("cleaned up"), 2)
        self.assertIn("-> 1 failures", result.stdout)
        self.assertIn("-> 1 successes", result.stdout)

    def test_unexpected_body_and_cleanup_exceptions_are_counted(self):
        result = self.compile_and_run('''
#include "littletest.hpp"
LT_BEGIN_SUITE(S)
void tear_down() { throw 23; }
LT_END_SUITE(S)
LT_BEGIN_TEST(S,T)
throw 17;
LT_END_TEST(T)
''' + AUTO_MAIN)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("-> 2 failures", result.stdout)

    def test_nothrow_reports_standard_and_nonstandard_exceptions(self):
        result = self.run_test_body('''
LT_CHECK_NOTHROW(throw std::runtime_error("useful detail"));
LT_CHECK_NOTHROW(throw 7);
LT_CHECK_THROW(throw std::runtime_error("expected"));
LT_CHECK_THROW(throw 7);
''')
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("useful detail", result.stdout)
        self.assertIn("-> 2 failures", result.stdout)
        self.assertIn("-> 2 successes", result.stdout)

    def test_comparisons_accept_temporaries_and_noncopyable_values(self):
        result = self.run_test_body('''
Noncopyable a;
LT_CHECK_EQ(a,a);
LT_CHECK_EQ(Noncopyable(),Noncopyable());
LT_CHECK_EQ(std::string("hello"),std::string("hello"));
LT_CHECK_NEQ(1,2);
LT_CHECK_GT(2,1);
LT_CHECK_GTE(2,2);
LT_CHECK_LT(1,2);
LT_CHECK_LTE(2,2);
''', includes='''
#include <ostream>
struct Noncopyable {
    Noncopyable() = default;
    Noncopyable(const Noncopyable&) = delete;
};
bool operator==(const Noncopyable&, const Noncopyable&) { return true; }
std::ostream& operator<<(std::ostream& s, const Noncopyable&) { return s << "value"; }
''')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("-> 8 successes", result.stdout)

    def test_legacy_collection_checks_still_work(self):
        result = self.run_test_body('''
int a[] = {1,2}, b[] = {1,3};
LT_CHECK_COLLECTIONS_EQ(a,a+1,b);
LT_CHECK_COLLECTIONS_NEQ(a,a+2,b);
LT_ASSERT_COLLECTIONS_EQ(a,a,a);
LT_WARN_COLLECTIONS_EQ(a,a+2,b);
''')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("-> 3 successes", result.stdout)
        self.assertIn("[WARN]", result.stdout)

    def test_bounded_collections_reject_unequal_contents(self):
        result = self.run_test_body('''
int a[] = {1,2}, b[] = {1,3};
LT_CHECK_COLLECTIONS_EQ(a,a+2,b,b+2);
LT_CHECK_COLLECTIONS_NEQ(a,a+2,b,b+2);
LT_CHECK_COLLECTIONS_NEQ(a,a+2,a,a+2);
LT_CHECK_COLLECTIONS_NEQ(a,a,a,a);
''')
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("-> 3 failures", result.stdout)
        self.assertIn("-> 1 successes", result.stdout)

    def test_current_test_checkpoint_is_reported(self):
        result = self.run_test_body('''
LT_CHECKPOINT();
throw std::runtime_error("after checkpoint");
''')
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Last checkpoint", result.stdout)

    def test_empty_environment_reports_zero_averages(self):
        result = self.compile_and_run('#include "littletest.hpp"\n' + AUTO_MAIN)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("0 tests executed", result.stdout)
        self.assertIn("Average set up time: 0 ms", result.stdout)
        self.assertIn("Average tear down time: 0 ms", result.stdout)

    def test_manual_environment_aggregates_multiple_runners(self):
        result = self.run_test_body("LT_CHECK(false);", main='''
LT_BEGIN_TEST_ENV()
LT_CREATE_RUNNER(S,first);
LT_RUNNER(first)(T)();
LT_CREATE_RUNNER(S,second);
LT_RUNNER(second)();
LT_END_TEST_ENV()
''')
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("-> 1 failures", result.stdout)
        self.assertIn("-> 0 failures", result.stdout)


if __name__ == "__main__":
    unittest.main()
