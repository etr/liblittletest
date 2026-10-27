/*
     This file is part of liblittletest
     Copyright (C) 2012 Sebastiano Merlino

     This library is free software; you can redistribute it and/or
     modify it under the terms of the GNU Lesser General Public
     License as published by the Free Software Foundation; either
     version 2.1 of the License, or (at your option) any later version.

     This library is distributed in the hope that it will be useful,
     but WITHOUT ANY WARRANTY; without even the implied warranty of
     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
     Lesser General Public License for more details.

     You should have received a copy of the GNU Lesser General Public
     License along with this library; if not, write to the Free Software
     Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

*/

//TODO: personalized messages

#ifndef LITTLETEST_HPP_INCLUDED
#define LITTLETEST_HPP_INCLUDED

#include <string>
#include <iostream>
#include <sstream>
#include <algorithm>
#include <chrono>
#include <cstdlib>
#include <exception>
#include <vector>

#define LT_VERSION 1.0

#define LT_MODE_WARN 0
#define LT_MODE_CHECK 1
#define LT_MODE_ASSERT 2

#define LT_BEGIN_TEST_ENV() int main() { \
    littletest::detail::environment_failed() = false;

#define LT_END_TEST_ENV() \
    return littletest::detail::environment_failed() ? EXIT_FAILURE : EXIT_SUCCESS; \
    }

#define LT_BEGIN_AUTO_TEST_ENV() LT_BEGIN_TEST_ENV()

#define LT_END_AUTO_TEST_ENV() LT_END_TEST_ENV()

#define AUTORUN_TESTS() littletest::run_auto_tests();

#define LT_CREATE_RUNNER(lt_suite_name_, lt_runner_name_) \
    std::cout << "** Initializing Runner \"" << #lt_runner_name_ << "\" **" << std::endl; \
    littletest::test_runner lt_runner_name_

#define LT_RUNNER(lt_runner_name_) lt_runner_name_

#define LT_BEGIN_SUITE(lt_name_) \
    struct lt_name_ : public littletest::suite<lt_name_> \
    {

#define LT_END_SUITE(lt_name_) \
    };

#define LT_CHECKPOINT() lt_tr_->set_checkpoint(__FILE__, __LINE__)

#define LT_BEGIN_TEST(lt_suite_name_, lt_test_name_) \
    struct lt_test_name_ ## _class: public lt_suite_name_, littletest::test<lt_test_name_ ## _class> \
    { \
            lt_test_name_ ## _class() \
            { \
                lt_name_ = #lt_test_name_; \
                littletest::auto_test_vector().push_back(this); \
            } \
            void operator()(littletest::test_runner* lt_tr_) \
            {

#define LT_END_TEST(lt_test_name_) \
            } \
    }; \
    lt_test_name_ ## _class lt_test_name_; \

#define LT_BEGIN_AUTO_TEST(lt_suite_name_, lt_test_name_) LT_BEGIN_TEST(lt_suite_name_, lt_test_name_)

#define LT_END_AUTO_TEST(lt_test_name_) \
    LT_END_TEST(lt_test_name_) \

#define LT_SWITCH_MODE(lt_mode_) \
        switch(lt_mode_) \
        { \
            case(LT_MODE_WARN): \
                throw littletest::warn_unattended(lt_ss_.str()); \
            case(LT_MODE_CHECK): \
                throw littletest::check_unattended(lt_ss_.str()); \
            case(LT_MODE_ASSERT): \
                throw littletest::assert_unattended(lt_ss_.str()); \
        }

#define LT_SIMPLE_OP(lt_name_, lt_val_, lt_file_, lt_line_, lt_mode_) \
    if(!((lt_val_))) \
    { \
        std::stringstream lt_ss_; \
        lt_ss_ << "(" << lt_file_ << ":" << lt_line_ << ") - error in " << "\"" << lt_name_ << "\""; \
        LT_SWITCH_MODE(lt_mode_) \
    }

#define LT_THROW_OP(lt_name_, lt_operation_, lt_file_, lt_line_, lt_mode_) \
    if(![&]() { \
        try { (lt_operation_); } \
        catch(...) { return true; } \
        return false; \
    }()) \
    { \
        std::stringstream lt_ss_; \
        lt_ss_ << "(" << lt_file_ << ":" << lt_line_ << ") - error in " << "\"" << lt_name_ << "\": no exceptions thown by " << #lt_operation_; \
        LT_SWITCH_MODE(lt_mode_) \
    }

#define LT_NOTHROW_OP(lt_name_, lt_operation_, lt_file_, lt_line_, lt_mode_) \
    try \
    { \
        (lt_operation_) ;\
    } \
    catch(std::exception& e) \
    { \
        std::stringstream lt_ss_; \
        lt_ss_ << "(" << lt_file_ << ":" << lt_line_ << ") - error in " << "\"" << lt_name_ << "\": exceptions thown by " << #lt_operation_; \
        lt_ss_ << " [ " << e.what() << " ]"; \
        LT_SWITCH_MODE(lt_mode_) \
    } \
    catch(...) \
    { \
        std::stringstream lt_ss_; \
        lt_ss_ << "(" << lt_file_ << ":" << lt_line_ << ") - error in " << "\"" << lt_name_ << "\": exceptions thown by " << #lt_operation_; \
        LT_SWITCH_MODE(lt_mode_) \
    }

#define LT_DETAIL_JOIN_IMPL(lt_prefix_, lt_suffix_) lt_prefix_ ## lt_suffix_
#define LT_DETAIL_JOIN(lt_prefix_, lt_suffix_) LT_DETAIL_JOIN_IMPL(lt_prefix_, lt_suffix_)

// Generate operand bindings per invocation without changing evaluation or lifetime.
#define LT_OP(lt_name_, lt_a_, lt_b_, lt_file_, lt_line_, lt_op_, lt_mode_) \
    LT_OP_IMPL(lt_name_, lt_a_, lt_b_, lt_file_, lt_line_, lt_op_, lt_mode_, \
        LT_DETAIL_JOIN(lt_comparison_left_at_line_, __LINE__), \
        LT_DETAIL_JOIN(lt_comparison_right_at_line_, __LINE__))

#define LT_OP_IMPL(lt_name_, lt_a_, lt_b_, lt_file_, lt_line_, lt_op_, lt_mode_, lt_left_local_, lt_right_local_) \
    const auto& lt_left_local_ = (lt_a_); \
    const auto& lt_right_local_ = (lt_b_); \
    if(!(lt_left_local_ lt_op_ lt_right_local_)) \
    { \
        std::stringstream lt_ss_; \
        lt_ss_ << "(" << lt_file_ << ":" << lt_line_ << ") - error in " << "\"" << lt_name_ << "\": " << lt_left_local_ << " " << #lt_op_ << " " << lt_right_local_; \
        LT_SWITCH_MODE(lt_mode_) \
    }

#define LT_CATCH_ERRORS \
    catch(littletest::check_unattended& lt_cu_) \
    { \
        std::cout << "[CHECK FAILURE] " << lt_cu_.what() << std::endl; \
        lt_tr_->add_failure(); \
    } \
    catch(littletest::assert_unattended& lt_au_) \
    { \
        std::cout << "[ASSERT FAILURE] " << lt_au_.what() << std::endl; \
        lt_tr_->add_failure(); \
        throw lt_au_; \
    } \
    catch(littletest::warn_unattended& lt_wu_) \
    { \
        std::cout << "[WARN] " << lt_wu_.what() << std::endl; \
    }

#define LT_ADD_SUCCESS(lt_mode_) \
    if(lt_mode_) \
        lt_tr_->add_success();

#define LT_EV(lt_a_, lt_b_, lt_op_, lt_mode_) \
    do { \
        try \
        { \
            LT_OP(lt_name_, (lt_a_), (lt_b_), __FILE__, __LINE__, lt_op_, lt_mode_); \
            LT_ADD_SUCCESS(lt_mode_) \
        } \
        LT_CATCH_ERRORS \
    } while(false)

#define LT_SIMPLE_EV(lt_val_, lt_mode_) \
    do { \
        try \
        { \
            LT_SIMPLE_OP(lt_name_, (lt_val_), __FILE__, __LINE__, lt_mode_); \
            LT_ADD_SUCCESS(lt_mode_) \
        } \
        LT_CATCH_ERRORS \
    } while(false)

#define LT_THROW_EV(lt_operation_, lt_mode_) \
    do { \
        try \
        { \
            LT_THROW_OP(lt_name_, (lt_operation_), __FILE__, __LINE__, lt_mode_); \
            LT_ADD_SUCCESS(lt_mode_) \
        } \
        LT_CATCH_ERRORS \
    } while(false)

#define LT_NOTHROW_EV(lt_operation_, lt_mode_) \
    do { \
        try \
        { \
            LT_NOTHROW_OP(lt_name_, (lt_operation_), __FILE__, __LINE__, lt_mode_); \
            LT_ADD_SUCCESS(lt_mode_) \
        } \
        LT_CATCH_ERRORS \
    } while(false)

#define LT_COLLECTION_EV(lt_expected_, lt_mode_, ...) \
    do { \
        try \
        { \
            if(littletest::detail::collections_equal(__VA_ARGS__) != (lt_expected_)) \
            { \
                std::stringstream lt_ss_; \
                lt_ss_ << "(" << __FILE__ << ":" << __LINE__ << ") - error in " \
                    << "\"" << lt_name_ << "\": collections are " \
                    << ((lt_expected_) ? "different" : "equal"); \
                LT_SWITCH_MODE(lt_mode_) \
            } \
            LT_ADD_SUCCESS(lt_mode_) \
        } \
        LT_CATCH_ERRORS \
    } while(false)

#define LT_WARN(lt_val_) LT_SIMPLE_EV((lt_val_), LT_MODE_WARN)
#define LT_WARN_EQ(lt_a_, lt_b_) LT_EV((lt_a_), (lt_b_), ==, LT_MODE_WARN)
#define LT_WARN_NEQ(lt_a_, lt_b_) LT_EV((lt_a_), (lt_b_), !=, LT_MODE_WARN)
#define LT_WARN_GT(lt_a_, lt_b_) LT_EV((lt_a_), (lt_b_), >, LT_MODE_WARN)
#define LT_WARN_GTE(lt_a_, lt_b_) LT_EV((lt_a_), (lt_b_), >=, LT_MODE_WARN)
#define LT_WARN_LT(lt_a_, lt_b_) LT_EV((lt_a_), (lt_b_), <, LT_MODE_WARN)
#define LT_WARN_LTE(lt_a_, lt_b_) LT_EV((lt_a_), (lt_b_), <=, LT_MODE_WARN)
#define LT_WARN_THROW(lt_operation_) LT_THROW_EV((lt_operation_), LT_MODE_WARN)
#define LT_WARN_NOTHROW(lt_operation_) LT_NOTHROW_EV((lt_operation_), LT_MODE_WARN)
#define LT_WARN_COLLECTIONS_EQ(...) LT_COLLECTION_EV(true, LT_MODE_WARN, __VA_ARGS__)
#define LT_WARN_COLLECTIONS_NEQ(...) LT_COLLECTION_EV(false, LT_MODE_WARN, __VA_ARGS__)

#define LT_CHECK(lt_val_) LT_SIMPLE_EV((lt_val_), LT_MODE_CHECK)
#define LT_CHECK_EQ(lt_a_, lt_b_) LT_EV((lt_a_), (lt_b_), ==, LT_MODE_CHECK)
#define LT_CHECK_NEQ(lt_a_, lt_b_) LT_EV((lt_a_), (lt_b_), !=, LT_MODE_CHECK)
#define LT_CHECK_GT(lt_a_, lt_b_) LT_EV((lt_a_), (lt_b_), >, LT_MODE_CHECK)
#define LT_CHECK_GTE(lt_a_, lt_b_) LT_EV((lt_a_), (lt_b_), >=, LT_MODE_CHECK)
#define LT_CHECK_LT(lt_a_, lt_b_) LT_EV((lt_a_), (lt_b_), <, LT_MODE_CHECK)
#define LT_CHECK_LTE(lt_a_, lt_b_) LT_EV((lt_a_), (lt_b_), <=, LT_MODE_CHECK)
#define LT_CHECK_THROW(lt_operation_) LT_THROW_EV((lt_operation_), LT_MODE_CHECK)
#define LT_CHECK_NOTHROW(lt_operation_) LT_NOTHROW_EV((lt_operation_), LT_MODE_CHECK)
#define LT_CHECK_COLLECTIONS_EQ(...) LT_COLLECTION_EV(true, LT_MODE_CHECK, __VA_ARGS__)
#define LT_CHECK_COLLECTIONS_NEQ(...) LT_COLLECTION_EV(false, LT_MODE_CHECK, __VA_ARGS__)

#define LT_ASSERT(lt_val_) LT_SIMPLE_EV((lt_val_), LT_MODE_ASSERT)
#define LT_ASSERT_EQ(lt_a_, lt_b_) LT_EV((lt_a_), (lt_b_), ==, LT_MODE_ASSERT)
#define LT_ASSERT_NEQ(lt_a_, lt_b_) LT_EV((lt_a_), (lt_b_), !=, LT_MODE_ASSERT)
#define LT_ASSERT_GT(lt_a_, lt_b_) LT_EV((lt_a_), (lt_b_), >, LT_MODE_ASSERT)
#define LT_ASSERT_GTE(lt_a_, lt_b_) LT_EV((lt_a_), (lt_b_), >=, LT_MODE_ASSERT)
#define LT_ASSERT_LT(lt_a_, lt_b_) LT_EV((lt_a_), (lt_b_), <, LT_MODE_ASSERT)
#define LT_ASSERT_LTE(lt_a_, lt_b_) LT_EV((lt_a_), (lt_b_), <=, LT_MODE_ASSERT)
#define LT_ASSERT_THROW(lt_operation_) LT_THROW_EV((lt_operation_), LT_MODE_ASSERT)
#define LT_ASSERT_NOTHROW(lt_operation_) LT_NOTHROW_EV((lt_operation_), LT_MODE_ASSERT)
#define LT_ASSERT_COLLECTIONS_EQ(...) LT_COLLECTION_EV(true, LT_MODE_ASSERT, __VA_ARGS__)
#define LT_ASSERT_COLLECTIONS_NEQ(...) LT_COLLECTION_EV(false, LT_MODE_ASSERT, __VA_ARGS__)

#define LT_FAIL(lt_message_) \
    do { \
        std::cout << "[ASSERT FAILURE] (" << __FILE__ << ":" << __LINE__ << ") - error in " << "\"" << (lt_name_) << "\": " << (lt_message_) << std::endl; \
        lt_tr_->add_failure(); \
        throw littletest::assert_unattended(""); \
    } while(false)

namespace littletest
{

struct check_unattended : public std::exception
{
    check_unattended(const std::string& message):
        message(message)
    {
    }
    ~check_unattended() throw() { }

    virtual const char* what() const throw()
    {
        return message.c_str();
    }

    private:
        std::string message;
};

struct assert_unattended : public std::exception
{
    assert_unattended(const std::string& message):
        message(message)
    {
    }
    ~assert_unattended() throw() { }
    virtual const char* what() const throw()
    {
        return message.c_str();
    }

    private:
        std::string message;
};

struct warn_unattended : public std::exception
{
    warn_unattended(const std::string& message):
        message(message)
    {
    }
    ~warn_unattended() throw() { }
    virtual const char* what() const throw()
    {
        return message.c_str();
    }

    private:
        std::string message;
};

template <class suite_impl>
class suite
{
    public:
        void set_up() {}
        void tear_down() {}

        void suite_set_up()
        {
            static_cast<suite_impl*>(this)->set_up();
        }

        void suite_tear_down()
        {
            static_cast<suite_impl*>(this)->tear_down();
        }

        suite() { }
        suite(const suite<suite_impl>& s) { }
};

typedef std::chrono::steady_clock clock;

inline double calculate_duration(const clock::time_point& before, const clock::time_point& after)
{
    return std::chrono::duration<double, std::milli>(after - before).count();
}

namespace detail
{
    template <class First, class Second>
    bool collections_equal(First first, First last, Second second)
    {
        // Legacy overload: the second range must contain at least as many elements.
        return std::equal(first, last, second);
    }

    template <class First, class Second>
    bool collections_equal(First first, First last, Second second, Second second_last)
    {
        for(; first != last && second != second_last; ++first, ++second)
            if(!(*first == *second))
                return false;
        return first == last && second == second_last;
    }

    inline bool& environment_failed()
    {
        // Sticky across runner summaries; reset only when the environment begins.
        static bool failed = false;
        return failed;
    }
}

class test_base;

inline std::vector<test_base*>& auto_test_vector()
{
    static std::vector<test_base*> tests;
    return tests;
}

class test_runner
{
    public:
        test_runner() :
            last_checkpoint_file(""),
            last_checkpoint_line(-1),
            test_counter(1),
            success_counter(0),
            failures_counter(0),
            good_time_total(0.0),
            total_set_up_time(0.0),
            total_tear_down_time(0.0),
            total_time(0.0)
        {
        }

        template <class test_impl>
        test_runner& run(test_impl* t)
        {
            std::cout << "Running test (" <<
                test_counter << "): " <<
                t->lt_name_ << std::endl;

            last_checkpoint_file.clear();
            last_checkpoint_line = -1;
            t->run_test(this);

            test_counter++;
            return *this;
        }

        template <class test_impl>
        test_runner& operator()(test_impl& t)
        {
            return run(&t);
        }

        template <class test_impl>
        test_runner& operator()(test_impl* t)
        {
            return run(t);
        }

        void clear_runner()
        {
            last_checkpoint_file = "";
            last_checkpoint_line = -1;
            test_counter = 1;
            success_counter = 0;
            failures_counter = 0;
            good_time_total = 0.0;
            total_set_up_time = 0.0;
            total_tear_down_time = 0.0;
            total_time = 0.0;
        }

        int operator()()
        {
            std::cout << "** Runner terminated! **" << std::endl;
            std::cout << (test_counter - 1) << " tests executed" << std::endl;
            std::cout << (failures_counter + success_counter) << " checks" << std::endl;
            std::cout << "-> " << success_counter << " successes" << std::endl;
            std::cout << "-> " << failures_counter << " failures" << std::endl;
            std::cout << "Total run time: " << total_time << " ms"<< std::endl;
            std::cout << "Total time spent in tests: " << good_time_total << " ms" << std::endl;
            const int completed = test_counter - 1;
            std::cout << "Average set up time: " << (completed ? total_set_up_time / completed : 0.0) << " ms" << std::endl;
            std::cout << "Average tear down time: " << (completed ? total_tear_down_time / completed : 0.0) << " ms" << std::endl;
            int to_ret = failures_counter;
            clear_runner();
            return to_ret;
        }

        void add_failure()
        {
            failures_counter++;
            detail::environment_failed() = true;
        }

        void add_success()
        {
            success_counter++;
        }

        void set_checkpoint(const char* file, int line)
        {
            last_checkpoint_file = file;
            last_checkpoint_line = line;
        }

        void add_good_time(double t)
        {
            good_time_total += t;
        }

        void add_set_up_time(double t)
        {
            total_set_up_time += t;
        }

        void add_tear_down_time(double t)
        {
            total_tear_down_time += t;
        }

        void add_total_time(double t)
        {
            total_time += t;
        }

        operator int()
        {
            return failures_counter;
        }

        int get_test_number()
        {
            return test_counter;
        }

        int get_successes()
        {
            return success_counter;
        }

        int get_failures()
        {
            return failures_counter;
        }

        double get_test_time()
        {
            return good_time_total;
        }

        double get_total_time()
        {
            return total_time;
        }

        std::string last_checkpoint_file;
        int last_checkpoint_line;

    private:
        int test_counter;
        int success_counter;
        int failures_counter;
        double good_time_total;
        double total_set_up_time;
        double total_tear_down_time;
        double total_time;
};

class test_base
{
    public:
        const char* lt_name_;
        virtual void run_test(test_runner* tr) { }
        virtual void operator()() { }
};

inline test_runner& auto_test_runner()
{
    static test_runner runner;
    return runner;
}

inline int run_auto_tests()
{
    for(test_base* t : auto_test_vector())
        auto_test_runner()(t);
    return auto_test_runner()();
}

template <class test_impl>
class test : public test_base
{
        virtual void run_test(test_runner* tr)
        {
            double set_up_duration = 0.0, tear_down_duration = 0.0, test_duration = 0.0;
            clock::time_point before, after;
            bool setup_succeeded = false;
            before = clock::now();
            try
            {
                static_cast<test_impl* >(this)->suite_set_up();
                setup_succeeded = true;
            }
            catch(std::exception& e)
            {
                std::cout << "[FAILURE] Exception during " << static_cast<test_impl* >(this)->lt_name_ << " set up" << std::endl;
                std::cout << e.what() << std::endl;
                tr->add_failure();
            }
            catch(...)
            {
                std::cout << "[FAILURE] Exception during " << static_cast<test_impl* >(this)->lt_name_ << " set up" << std::endl;
                tr->add_failure();
            }
            after = clock::now();
            set_up_duration = calculate_duration(before, after);
            tr->add_set_up_time(set_up_duration);
            before = clock::now();
            try
            {
                if(setup_succeeded)
                    (*static_cast<test_impl*>(this))(tr);
            }
            catch(assert_unattended& au)
            {
                ;
            }
            catch(std::exception& e)
            {
                std::cout << "[FAILURE] Exception during " << static_cast<test_impl* >(this)->lt_name_ << " run" << std::endl;
                std::cout << e.what() << std::endl;
                if(tr->last_checkpoint_line != -1)
                    std::cout << "Last checkpoint in " << tr->last_checkpoint_file << ":" << tr->last_checkpoint_line << std::endl;
                tr->add_failure();
            }
            catch(...)
            {
                std::cout << "[FAILURE] Exception during " << static_cast<test_impl* >(this)->lt_name_ << " run" << std::endl;
                if(tr->last_checkpoint_line != -1)
                    std::cout << "Last checkpoint in " << tr->last_checkpoint_file << ":" << tr->last_checkpoint_line << std::endl;
                tr->add_failure();
            }
            after = clock::now();

            test_duration = calculate_duration(before, after);

            tr->add_good_time(test_duration);

            std::cout << "- Time spent during \"" << static_cast<test_impl* >(this)->lt_name_ << "\": " << test_duration << " ms"<< std::endl;

            try
            {
                before = clock::now();
                static_cast<test_impl* >(this)->suite_tear_down();
            }
            catch(std::exception& e)
            {
                std::cout << "[FAILURE] Exception during " << static_cast<test_impl* >(this)->lt_name_ << " tear down" << std::endl;
                std::cout << e.what() << std::endl;
                tr->add_failure();
            }
            catch(...)
            {
                std::cout << "[FAILURE] Exception during " << static_cast<test_impl* >(this)->lt_name_ << " tear down" << std::endl;
                tr->add_failure();
            }
            after = clock::now();
            tear_down_duration = calculate_duration(before, after);
            tr->add_tear_down_time(tear_down_duration);
            double total = set_up_duration + test_duration + tear_down_duration;
            tr->add_total_time(total);
        }
    protected:
        test() { }
        test(const test<test_impl>& t) { }

        friend class test_runner;
};

}

#endif //LITTLETEST_HPP_INCLUDED
