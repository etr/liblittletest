liblittletest
=============
A complete unit testing framework in a header

liblittletest is an easy to use all-in-an-header testing framework; all you have to do in order to use it is to include the header in your code.

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

## Running Tests (the manual way)
### Tests
A test is an entity containing the used to check your applications. If you plan to run your tests manually you have to initialize your tests this way:

    LT_BEGIN_TEST(suite_name, test_name)
        ...
    LT_END_TEST(test_name)

As you can see, the suite_name is the first parameter specified and so the test "inherits" set_up and tear_down methods and is able to use each attribute defined inside the suite.

### Runners and Environment
Tests are performed by runners. A runner is an object that not only runs tests but also collects all informations about successes and failures and also about timings. Is up to the runner to execute set_up and tear_down methods.

Each runner is specialized to work with tests of a particular suite and it is not possible with a single runner to execute tests of different suites.

A runner can live only inside an environment.

    LT_BEGIN_TEST_ENV()
        LT_CREATE_RUNNER(suite_name, runner_name);
        LT_RUNNER(runner_name)(test_1)(test_2)(test_3)();
    LT_END_TEST_ENV()

In the previous example a test environment is created and a runner is initialized. The three tests, test_1, test_2 and test_3 are registered and the runner is executed.

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
* LT_CHECK_COLLECTIONS_EQ(first1, last1, first2) : the check succeeds if collections a and b are equal;
* LT_CHECK_COLLECTIONS_NEQ(first1, last1, first2) : the check succeeds if collections a and b are not equal;

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
* LT_WARN_COLLECTIONS_EQ(first1, last1, first2) : the check succeeds if collections a and b are equal;
* LT_WARN_COLLECTIONS_NEQ(first1, last1, first2) : the check succeeds if collections a and b are not equal;

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
* LT_ASSERT_COLLECTIONS_EQ(first1, last1, first2) : the check succeeds if collections a and b are equal;
* LT_ASSERT_COLLECTIONS_NEQ(first1, last1, first2) : the check succeeds if collections a and b are not equal;

### Checkpoints
Sometimes a code may generate uncaught exceptions that the executing runner catches and reports. In these cases may be useful to know which was the last checkpoint the executor passed through.

You can set a checkpoint inside your tests using the macro:

    LT_CHECKPOINT()

### Piloted Failures
It maybe useful sometimes to generate a failure manually. This is always possible to do this by the use of the macro:

    LT_FAIL(message)

This will generate a failure equal to that emitted by a failed assert printing out the specified message.
