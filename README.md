liblittletest
=============
A complete unit testing framework in a header

liblittletest is an easy to use all-in-an-header testing framework; all you have to do in order to use it is to include the header in your code.

Requires C++11 or later and the standard library. Include `src/littletest.hpp`;
there is no library to build or link and no implementation macro to define.
For example: `c++ -std=c++11 -Isrc tests.cpp -o tests`.
The header can be included in multiple source files in the same test executable.
Define the test environment (which supplies `main`) in exactly one source file,
and give tests unique names within their namespace.

Download [littletest.hpp for v2.1.0](https://github.com/etr/liblittletest/releases/download/v2.1.0/littletest.hpp)
or see the [release notes](https://github.com/etr/liblittletest/releases/tag/v2.1.0).
`LT_VERSION` is the numeric major/minor version (`2.1`);
`LT_VERSION_STRING` contains the full version (`"2.1.0"`).

Version 2.1.0 adds richer diagnostics and optional messages, command-line test
listing and filtering, typed exception checks, and explicit-tolerance near
comparisons. It retains C++11 support and the single-header distribution.

# How to use
## Preparing Tests
### Suites
A suite represents a model for tests; it defines set_up and tear_down methods used in all the tests which refer to the suite. All suite attributes are directly usable by its tests.

A suite can be defined in this way:

    LT_BEGIN_SUITE(suite_name)
    ...attributes....
    void set_up()
    {
        ...
    }

    void tear_down()
    {
        ...
    }
    LT_END_SUITE(suite_name)

It is possible to define a suite without specifying set_up or tear_down methods. 
set_up and tear_down methods are called respectively before and after each test.
If `set_up()` throws, the failure is recorded and the test body is skipped.
`tear_down()` is still attempted, including after a failed setup or assertion, so
it must tolerate partially initialized state. Exceptions from the test body or
cleanup are also recorded as failures, and later tests continue running.

## Running Tests (the manual way)
### Tests
A test is an entity containing the used to check your applications. If you plan to run your tests manually you have to initialize your tests this way:

    LT_BEGIN_TEST(suite_name, test_name)
        ...
    LT_END_TEST(test_name)

As you can see, the suite_name is the first parameter specified and so the test "inherits" set_up and tear_down methods and is able to use each attribute defined inside the suite.

### Runners and Environment
Tests are performed by runners. A runner is an object that not only runs tests but also collects all informations about successes and failures and also about timings. Is up to the runner to execute set_up and tear_down methods.

One runner can execute tests from different suites.

A runner can live only inside an environment.

    LT_BEGIN_TEST_ENV()
        LT_CREATE_RUNNER(suite_name, runner_name);
        LT_RUNNER(runner_name)(test_1)(test_2)(test_3)();
    LT_END_TEST_ENV()

In the previous example a test environment is created and a runner is initialized. The three tests, test_1, test_2 and test_3 are registered and the runner is executed.

Tests execute as they are passed to the runner; the final `()` prints a summary,
returns its failure count, and clears the runner's counters. The environment
remembers failures across summaries and runners and returns `EXIT_FAILURE` if
any check, assertion, or unexpected exception failed; otherwise it returns
`EXIT_SUCCESS`. Warnings do not affect the exit status. Automatic environments
use the same rule, including when the failure count is a multiple of 256.

If you write your own `main()` instead, normalize the summary result explicitly:

    int failures = runner();
    return failures ? EXIT_FAILURE : EXIT_SUCCESS;

Timings use `std::chrono::steady_clock` and are reported in milliseconds.

## Running Tests (the automatic way)
### Tests
Sometimes a manual management of tests running is not necessary and only disturbing. If you do not need to manage manually your tests, you can write your tests this way:

    LT_BEGIN_AUTO_TEST(suite_name, test_name)
        ...
    LT_END_AUTO_TEST(test_name)

The syntax of the macro is the same apart of the "AUTO" prefix.

### Runners and Environment
Also in this case, tests are executed by a runner and inside an environment, but it is all easier to do (compared to the previous version). The sole thing you have to do is:

    LT_BEGIN_AUTO_TEST_ENV()
        AUTORUN_TESTS()
    LT_END_AUTO_TEST_ENV()

### Listing and selecting tests

Both manual and automatic environments accept these command-line options without
changing their macro call sites:

    ./tests --list
    ./tests --filter "parser*"
    ./tests --list --filter="parser?"

Patterns match the entire test name, are case-sensitive, and support `*` for any
number of characters and `?` for one character. Other characters are literal;
there is no regular-expression or bracket syntax. Quote patterns to prevent the
shell from expanding them. Missing, empty, repeated, or unknown options produce a
usage error; repeated `--list` is harmless.

`--list` prints registered test names and exits before executing the environment
body or any fixtures or tests. Define tests at namespace scope. In a manual
environment, listing shows all registered tests, while execution still runs only
the tests explicitly passed to its runners, in their original order. A filter can
remove tests from that selection but cannot add others. A supplied filter that
selects no tests to execute (or no names to list) returns a failure status.
Without options, existing execution behavior is preserved, including successful
empty environments. Hand-written `main()` functions do not parse these options
automatically.

## Tests Content
### Controls
**Checks**

Checks are simple controls. A failed check represents a failure for the runner and, otherwise, a succeeded check represents a success.

* LT_CHECK(expr) : the check succeeds if expr returns true;
* LT_CHECK_MSG(expr, message) : the check succeeds if expr returns true; evaluates and prints message only on failure;
* LT_CHECK_EQ(a,b) : the check succeeds if a is equal to b;
* LT_CHECK_NEQ(a,b) : the check succeeds if a is not equal to b;
* LT_CHECK_GT(a, b) : the check succeeds if a is greater than b;
* LT_CHECK_GTE(a, b) : the check succeeds if a is greater or equal to b;
* LT_CHECK_LT(a, b) : the check succeeds if a is lesser than b;
* LT_CHECK_LTE(a, b) : the check succeeds if a is lessert or equal to b;
* LT_CHECK_NEAR(actual, expected, tolerance) : the check succeeds if the values are within the explicit absolute tolerance;
* LT_CHECK_THROW(expr) : the check succeeds if expr raises an exception;
* LT_CHECK_THROW_AS(expr, Type) : the check succeeds if expr raises an exception matching Type;
* LT_CHECK_NOTHROW(expr) : the check succeeds if expr does not raise an exception;
* LT_CHECK_COLLECTIONS_EQ(first1, last1, first2, last2) : the check succeeds if both ranges have equal lengths and elements;
* LT_CHECK_COLLECTIONS_NEQ(first1, last1, first2, last2) : the check succeeds if the ranges differ in length or elements;

**Warnings**

Warnings are used to signal that maybe a problem (but not that the test failed). A failed warn control does not represent a failure for the runner and, for the same reason, a succeeded warn control does not represent a success.

* LT_WARN(expr) : the check succeeds if expr returns true;
* LT_WARN_MSG(expr, message) : the warning succeeds if expr returns true; evaluates and prints message only on failure;
* LT_WARN_EQ(a,b) : the check succeeds if a is equal to b;
* LT_WARN_NEQ(a,b) : the check succeeds if a is not equal to b;
* LT_WARN_GT(a, b) : the check succeeds if a is greater than b;
* LT_WARN_GTE(a, b) : the check succeeds if a is greater or equal to b;
* LT_WARN_LT(a, b) : the check succeeds if a is lesser than b;
* LT_WARN_LTE(a, b) : the check succeeds if a is lessert or equal to b;
* LT_WARN_NEAR(actual, expected, tolerance) : the warning succeeds if the values are within the explicit absolute tolerance;
* LT_WARN_THROW(expr) : the check succeeds if expr raises an exception;
* LT_WARN_THROW_AS(expr, Type) : the warning succeeds if expr raises an exception matching Type;
* LT_WARN_NOTHROW(expr) : the check succeeds if expr does not raise an exception;
* LT_WARN_COLLECTIONS_EQ(first1, last1, first2, last2) : the warning succeeds if both ranges have equal lengths and elements;
* LT_WARN_COLLECTIONS_NEQ(first1, last1, first2, last2) : the warning succeeds if the ranges differ in length or elements;

**Asserts**

Asserts are serious controls that need to be satisfied in order to continue a test. When an assert is unattended the test must be interrupted and the next test is executed. A failed assert represents a failure for the runner and, otherwise, a succeeded assert represents a success.

* LT_ASSERT(expr) : the check succeeds if expr returns true;
* LT_ASSERT_MSG(expr, message) : the assertion succeeds if expr returns true; evaluates and prints message only on failure;
* LT_ASSERT_EQ(a,b) : the check succeeds if a is equal to b;
* LT_ASSERT_NEQ(a,b) : the check succeeds if a is not equal to b;
* LT_ASSERT_GT(a, b) : the check succeeds if a is greater than b;
* LT_ASSERT_GTE(a, b) : the check succeeds if a is greater or equal to b;
* LT_ASSERT_LT(a, b) : the check succeeds if a is lesser than b;
* LT_ASSERT_LTE(a, b) : the check succeeds if a is lessert or equal to b;
* LT_ASSERT_NEAR(actual, expected, tolerance) : the assertion succeeds if the values are within the explicit absolute tolerance;
* LT_ASSERT_THROW(expr) : the check succeeds if expr raises an exception;
* LT_ASSERT_THROW_AS(expr, Type) : the assertion succeeds if expr raises an exception matching Type;
* LT_ASSERT_NOTHROW(expr) : the check succeeds if expr does not raise an exception;
* LT_ASSERT_COLLECTIONS_EQ(first1, last1, first2, last2) : the assertion succeeds if both ranges have equal lengths and elements;
* LT_ASSERT_COLLECTIONS_NEQ(first1, last1, first2, last2) : the assertion succeeds if the ranges differ in length or elements;

All collection macros also accept the original three-iterator form
`(first1, last1, first2)`. That form compares the first range against an equally
long prefix starting at `first2`: the caller must ensure that the second range
contains at least that many elements. It cannot check the second range's length.
Prefer four iterators to compare complete collections safely. Both forms support
input iterators; the bounded form walks each range once.

Comparison operands are evaluated once, from left to right, and bound by const
reference for comparison and diagnostics. For example, a failed
`LT_CHECK_EQ(++i, 0)` increments `i` once. Ordered comparisons with `NaN` fail.
Assertion macros can be used as ordinary statements in `if`/`else` branches.

### Failure details and optional messages

Boolean failures include their source expression. Comparison failures include
both operand expressions and their actual values, in addition to the test name,
file, and line. Equality-comparable types need not define `operator<<`: values
without stream insertion are displayed as `<unprintable>`. Operand evaluation,
reference binding, and temporary lifetimes follow the existing comparison rules.

Add context to a boolean check with `LT_CHECK_MSG(condition, message)`,
`LT_WARN_MSG(condition, message)`, or `LT_ASSERT_MSG(condition, message)`:

    LT_CHECK_MSG(record.valid(), "while parsing record 42");

The condition is evaluated once. The message expression is evaluated and printed
only when the condition is false; it can be a string or another streamable value.
Messages without stream insertion use the same `<unprintable>` fallback.
These macros preserve the usual warning, continuing check, and aborting assertion
behavior.

### Expected exception types

    LT_CHECK_THROW_AS(parse(input), std::invalid_argument);

`LT_CHECK_THROW_AS(expression, Type)`, `LT_WARN_THROW_AS`, and `LT_ASSERT_THROW_AS`
evaluate the expression once and match exceptions using normal C++ catch rules:
a derived exception matches an expected base class, and non-class exceptions
such as `int` are supported. Use a type alias when the type contains commas.
Missing exceptions and unexpected types produce distinct failures; an unexpected
exception is consumed so a failed check can continue. Warnings remain nonfatal,
and failed assertions stop the test while still allowing fixture cleanup.
The original `*_THROW` macros continue to accept any exception type.

### Floating-point comparisons

    LT_CHECK_NEAR(actual, expected, 0.001);

`LT_CHECK_NEAR(actual, expected, tolerance)`, `LT_WARN_NEAR`, and `LT_ASSERT_NEAR`
use an explicit absolute tolerance: the absolute difference must be at most the
tolerance. Arguments must be arithmetic values, are evaluated once in the order
actual, expected, tolerance, and are converted to `long double` for comparison.
This avoids integral subtraction overflow; comparisons have the precision of
`long double` on the target platform.

The tolerance must be finite and nonnegative, even when the values are equal.
NaN in either value or the tolerance always fails. Equal infinities of the same
sign pass; unequal infinities and finite/infinite pairs fail. Zero tolerance
requires equality, and positive and negative zero compare equal. Failures show
the operand expressions, values, and tolerance.

### Checkpoints
Sometimes a code may generate uncaught exceptions that the executing runner catches and reports. In these cases may be useful to know which was the last checkpoint the executor passed through.

You can set a checkpoint inside your tests using the macro:

    LT_CHECKPOINT()

### Piloted Failures
It maybe useful sometimes to generate a failure manually. This is always possible to do this by the use of the macro:

    LT_FAIL(message)

This will generate a failure equal to that emitted by a failed assert printing out the specified message.

## Developing liblittletest

Run the regression suite with Python 3 and a C++ compiler:

    python3 -B -m unittest discover -s tests -v

Set `CXX` to choose the compiler and `CXXFLAGS` to add compiler/linker flags, for
example `CXX=clang++ CXXFLAGS='-fsanitize=address,undefined' python3 -B -m unittest discover -s tests -v`.
The suite compiles temporary executables, checks their diagnostics and exit
status, and verifies automatic registration across source files. Python is only
needed to run these development checks; users need only the header.

Compatibility notes: C++11 is now the minimum. Internal registry/runner globals
are now inline accessors (`auto_test_vector()` and `auto_test_runner()`), and
internal identifiers no longer use reserved double underscores. The generic
`WARN`, `CHECK`, and `ASSERT` macros have been replaced with `LT_MODE_WARN`,
`LT_MODE_CHECK`, and `LT_MODE_ASSERT`. Normal use through the documented test and
assertion macros requires no changes.

## License

Copyright (c) 2012-2026 Sebastiano Merlino. Licensed under the [MIT License](LICENSE).
The full license notice is also included in the header for standalone distribution.
