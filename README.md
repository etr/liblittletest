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

Download [littletest.hpp for v2.0.0](https://github.com/etr/liblittletest/releases/download/v2.0.0/littletest.hpp)
or see the [release notes](https://github.com/etr/liblittletest/releases/tag/v2.0.0).
`LT_VERSION` is the numeric major/minor version (`2.0`);
`LT_VERSION_STRING` contains the full version (`"2.0.0"`).

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

## Tests Content
### Controls
**Checks**

Checks are simple controls. A failed check represents a failure for the runner and, otherwise, a succeeded check represents a success.
* LT_CHECK(expr) : the check succeeds if expr returns true;
* LT_CHECK_EQ(a,b) : the check succeeds if a is equal to b;
* LT_CHECK_NEQ(a,b) : the check succeeds if a is not equal to b;
* LT_CHECK_GT(a, b) : the check succeeds if a is greater than b;
* LT_CHECK_GTE(a, b) : the check succeeds if a is greater or equal to b;
* LT_CHECK_LT(a, b) : the check succeeds if a is lesser than b;
* LT_CHECK_LTE(a, b) : the check succeeds if a is lessert or equal to b;
* LT_CHECK_THROW(expr) : the check succeeds if expr raises an exception;
* LT_CHECK_NOTHROW(expr) : the check succeeds if expr does not raise an exception;
* LT_CHECK_COLLECTIONS_EQ(first1, last1, first2, last2) : the check succeeds if both ranges have equal lengths and elements;
* LT_CHECK_COLLECTIONS_NEQ(first1, last1, first2, last2) : the check succeeds if the ranges differ in length or elements;

**Warnings**

Warnings are used to signal that maybe a problem (but not that the test failed). A failed warn control does not represent a failure for the runner and, for the same reason, a succeeded warn control does not represent a success.
* LT_WARN(expr) : the check succeeds if expr returns true;
* LT_WARN_EQ(a,b) : the check succeeds if a is equal to b;
* LT_WARN_NEQ(a,b) : the check succeeds if a is not equal to b;
* LT_WARN_GT(a, b) : the check succeeds if a is greater than b;
* LT_WARN_GTE(a, b) : the check succeeds if a is greater or equal to b;
* LT_WARN_LT(a, b) : the check succeeds if a is lesser than b;
* LT_WARN_LTE(a, b) : the check succeeds if a is lessert or equal to b;
* LT_WARN_THROW(expr) : the check succeeds if expr raises an exception;
* LT_WARN_NOTHROW(expr) : the check succeeds if expr does not raise an exception;
* LT_WARN_COLLECTIONS_EQ(first1, last1, first2, last2) : the warning succeeds if both ranges have equal lengths and elements;
* LT_WARN_COLLECTIONS_NEQ(first1, last1, first2, last2) : the warning succeeds if the ranges differ in length or elements;

**Asserts**

Asserts are serious controls that need to be satisfied in order to continue a test. When an assert is unattended the test must be interrupted and the next test is executed. A failed assert represents a failure for the runner and, otherwise, a succeeded assert represents a success.
* LT_ASSERT(expr) : the check succeeds if expr returns true;
* LT_ASSERT_EQ(a,b) : the check succeeds if a is equal to b;
* LT_ASSERT_NEQ(a,b) : the check succeeds if a is not equal to b;
* LT_ASSERT_GT(a, b) : the check succeeds if a is greater than b;
* LT_ASSERT_GTE(a, b) : the check succeeds if a is greater or equal to b;
* LT_ASSERT_LT(a, b) : the check succeeds if a is lesser than b;
* LT_ASSERT_LTE(a, b) : the check succeeds if a is lessert or equal to b;
* LT_ASSERT_THROW(expr) : the check succeeds if expr raises an exception;
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

    python3 tests/test_littletest.py -v

Set `CXX` to choose the compiler and `CXXFLAGS` to add compiler/linker flags, for
example `CXX=clang++ CXXFLAGS='-fsanitize=address,undefined' python3 tests/test_littletest.py`.
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
