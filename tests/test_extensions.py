"""Consumer-facing regressions for the small assertion extensions."""

from test_littletest import AUTO_MAIN, HeaderHarness


class DiagnosticTests(HeaderHarness):
    def test_boolean_failure_names_the_source_expression(self):
        result = self.run_test_body('int count = 0; LT_CHECK(count > 0);')
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("count > 0", result.stdout)
        self.assertIn("test0.cpp:", result.stdout)

    def test_comparison_failure_names_expressions_and_actual_values(self):
        result = self.run_test_body('int actual = 1, expected = 2; LT_CHECK_EQ(actual,expected);')
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("actual == expected", result.stdout)
        self.assertIn("1 == 2", result.stdout)

    def test_unprintable_noncopyable_comparisons_compile_and_report(self):
        result = self.run_test_body('''
Value a(1), b(2);
LT_CHECK_EQ(a,b);
LT_CHECK_EQ(Value(3),Value(3));
''', includes='''
struct Value {
    int number;
    explicit Value(int n) : number(n) {}
    Value(const Value&) = delete;
};
bool operator==(const Value& a, const Value& b) { return a.number == b.number; }
''')
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("<unprintable>", result.stdout)
        self.assertIn("-> 1 failures", result.stdout)
        self.assertIn("-> 1 successes", result.stdout)

    def test_messages_are_lazy_and_conditions_are_evaluated_once(self):
        result = self.run_test_body('''
int conditions = 0, messages = 0;
LT_CHECK_MSG(++conditions == 1, ++messages);
LT_CHECK_MSG(++conditions == 1, ++messages);
std::cout << "conditions=" << conditions << ", messages=" << messages << std::endl;
''')
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("conditions=2, messages=1", result.stdout)
        self.assertIn("++conditions == 1", result.stdout)

    def test_message_operands_are_not_shadowed_by_internal_streams(self):
        result = self.run_test_body('''
std::string lt_ss_ = "record 42";
if (true) LT_CHECK_MSG(false,lt_ss_); else LT_FAIL("wrong branch");
''')
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("record 42", result.stdout)

    def test_message_warning_does_not_fail_and_assertion_stops_body(self):
        result = self.run_test_body('''
LT_WARN_MSG(false,"warning context");
LT_ASSERT_MSG(false,"assertion context");
std::cout << "unreachable" << std::endl;
''')
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("warning context", result.stdout)
        self.assertIn("assertion context", result.stdout)
        self.assertIn("-> 1 failures", result.stdout)
        self.assertNotIn("unreachable", result.stdout)


class TypedExceptionTests(HeaderHarness):
    def test_expected_types_follow_normal_cpp_catch_rules(self):
        result = self.run_test_body('''
LT_CHECK_THROW_AS(throw std::invalid_argument("bad input"),std::exception);
LT_CHECK_THROW_AS(throw 7,int);
LT_ASSERT_THROW_AS(throw std::runtime_error("expected"),std::runtime_error);
''')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("-> 3 successes", result.stdout)

    def test_wrong_and_missing_exceptions_fail_but_checks_continue(self):
        result = self.run_test_body('''
LT_CHECK_THROW_AS(throw std::logic_error("wrong"),std::runtime_error);
LT_CHECK_THROW_AS(throw 7,std::runtime_error);
LT_CHECK_THROW_AS(0,std::runtime_error);
LT_CHECK(true);
''')
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("unexpected exception type", result.stdout)
        self.assertIn("no exception", result.stdout)
        self.assertIn("std::runtime_error", result.stdout)
        self.assertIn("-> 3 failures", result.stdout)
        self.assertIn("-> 1 successes", result.stdout)

    def test_operation_evaluates_once_and_is_a_single_statement(self):
        result = self.run_test_body('''
int lt_ss_ = 0;
if (true) LT_CHECK_THROW_AS(throw ++lt_ss_,int); else LT_FAIL("wrong branch");
LT_CHECK_EQ(lt_ss_,1);
''')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_warning_and_assertion_keep_their_failure_semantics(self):
        result = self.run_test_body('''
LT_WARN_THROW_AS(0,int);
LT_ASSERT_THROW_AS(throw 7,std::runtime_error);
std::cout << "unreachable" << std::endl;
''')
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("[WARN]", result.stdout)
        self.assertIn("-> 1 failures", result.stdout)
        self.assertNotIn("unreachable", result.stdout)


class NearTests(HeaderHarness):
    def test_absolute_tolerance_includes_the_boundary(self):
        result = self.run_test_body('''
LT_CHECK_NEAR(1.0,1.25,0.25);
LT_CHECK_NEAR(1.0,1.5,0.25);
LT_CHECK_NEAR(1,1,0);
''')
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("-> 1 failures", result.stdout)
        self.assertIn("-> 2 successes", result.stdout)
        self.assertIn("tolerance", result.stdout)

    def test_invalid_tolerances_fail_even_for_equal_values(self):
        result = self.run_test_body('''
double nan = std::numeric_limits<double>::quiet_NaN();
double inf = std::numeric_limits<double>::infinity();
LT_CHECK_NEAR(1.0,1.0,-1.0);
LT_CHECK_NEAR(1.0,1.0,nan);
LT_CHECK_NEAR(1.0,1.0,inf);
''', includes="#include <limits>\n")
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("-> 3 failures", result.stdout)

    def test_nan_operands_and_unequal_infinities_fail(self):
        result = self.run_test_body('''
double nan = std::numeric_limits<double>::quiet_NaN();
double inf = std::numeric_limits<double>::infinity();
LT_CHECK_NEAR(nan,nan,0.1);
LT_CHECK_NEAR(1.0,nan,0.1);
LT_CHECK_NEAR(nan,1.0,0.1);
LT_CHECK_NEAR(inf,-inf,0.1);
LT_CHECK_NEAR(inf,1.0,0.1);
LT_CHECK_NEAR(1.0,inf,0.1);
''', includes="#include <limits>\n")
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("-> 6 failures", result.stdout)

    def test_equal_infinities_and_signed_zero_pass(self):
        result = self.run_test_body('''
double inf = std::numeric_limits<double>::infinity();
LT_CHECK_NEAR(inf,inf,0.0);
LT_CHECK_NEAR(-inf,-inf,0.0);
LT_CHECK_NEAR(0.0,-0.0,0.0);
''', includes="#include <limits>\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_operands_and_tolerance_evaluate_once_in_order(self):
        result = self.run_test_body('''
std::string order;
auto actual = [&]() { order += "A"; return 1.0; };
auto expected = [&]() { order += "E"; return 2.0; };
auto tolerance = [&]() { order += "T"; return 0.1; };
if (true) LT_CHECK_NEAR(actual(),expected(),tolerance()); else LT_FAIL("wrong branch");
std::cout << "order=" << order << std::endl;
''')
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("order=AET", result.stdout)
        self.assertIn("actual()", result.stdout)
        self.assertIn("expected()", result.stdout)
        self.assertIn("tolerance()", result.stdout)

    def test_warnings_and_assertions_keep_their_failure_semantics(self):
        result = self.run_test_body('''
LT_WARN_NEAR(1.0,2.0,0.1);
LT_ASSERT_NEAR(1.0,2.0,0.1);
std::cout << "unreachable" << std::endl;
''')
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("[WARN]", result.stdout)
        self.assertIn("-> 1 failures", result.stdout)
        self.assertNotIn("unreachable", result.stdout)

    def test_integer_operands_do_not_overflow_during_subtraction(self):
        result = self.run_test_body('''
LT_CHECK_NEAR(std::numeric_limits<long long>::min(),
              std::numeric_limits<long long>::max(),0.0);
''', includes="#include <limits>\n")
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("-> 1 failures", result.stdout)
