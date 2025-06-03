import unittest
import collections

# Adjust import path if necessary. If running 'python -m unittest discover' from root project directory
# and 'lcm_app' is in PYTHONPATH or is the current directory, this should work.
# If 'lcm_app' is the root, then 'from calculator import ...' might be used.
# Assuming the tests are run such that 'lcm_app' is a package visible in sys.path.
try:
    from lcm_app.calculator import get_prime_factorization, calculate_lcm_from_factors, calculate_lcm
except ImportError: # Fallback for running directly or if lcm_app is not seen as a package root
    import sys
    import os
    # Go up one level to the directory containing 'lcm_app' then add 'lcm_app' to path
    # This is a bit of a hack for varying test environments.
    # Proper way is to ensure PYTHONPATH is set or project is installed.
    # current_dir = os.path.dirname(os.path.abspath(__file__)) # lcm_app/tests
    # parent_dir = os.path.dirname(current_dir) # lcm_app
    # sys.path.insert(0, os.path.dirname(parent_dir)) # directory containing lcm_app
    # from lcm_app.calculator import get_prime_factorization, calculate_lcm_from_factors, calculate_lcm

    # Simpler fallback if script is run from project root or calculator.py is directly accessible
    from calculator import get_prime_factorization, calculate_lcm_from_factors, calculate_lcm


class TestCalculator(unittest.TestCase):

    # Tests for get_prime_factorization(n)
    def test_get_prime_factorization_prime(self):
        self.assertEqual(get_prime_factorization(7), collections.Counter({7: 1}))
        self.assertEqual(get_prime_factorization(2), collections.Counter({2: 1}))
        self.assertEqual(get_prime_factorization(3), collections.Counter({3: 1}))
        self.assertEqual(get_prime_factorization(13), collections.Counter({13: 1}))

    def test_get_prime_factorization_composite(self):
        self.assertEqual(get_prime_factorization(12), collections.Counter({2: 2, 3: 1}))
        self.assertEqual(get_prime_factorization(30), collections.Counter({2: 1, 3: 1, 5: 1}))
        self.assertEqual(get_prime_factorization(100), collections.Counter({2: 2, 5: 2}))

    def test_get_prime_factorization_power_of_prime(self):
        self.assertEqual(get_prime_factorization(8), collections.Counter({2: 3}))
        self.assertEqual(get_prime_factorization(27), collections.Counter({3: 3}))
        self.assertEqual(get_prime_factorization(25), collections.Counter({5: 2}))

    def test_get_prime_factorization_one(self):
        self.assertEqual(get_prime_factorization(1), collections.Counter())

    def test_get_prime_factorization_large_number(self):
        self.assertEqual(get_prime_factorization(99), collections.Counter({3: 2, 11: 1}))
        self.assertEqual(get_prime_factorization(60), collections.Counter({2: 2, 3: 1, 5: 1}))


    def test_get_prime_factorization_value_error(self):
        with self.assertRaises(ValueError):
            get_prime_factorization(0)
        with self.assertRaises(ValueError):
            get_prime_factorization(-5)
        with self.assertRaises(ValueError):
            get_prime_factorization(-1)

    # Tests for calculate_lcm_from_factors(num1_factors, num2_factors)
    def test_calculate_lcm_from_factors_simple(self):
        # Factors of 4 (2^2) and 6 (2^1 * 3^1) -> LCM should be 12 (2^2 * 3^1)
        factors4 = collections.Counter({2: 2})
        factors6 = collections.Counter({2: 1, 3: 1})
        self.assertEqual(calculate_lcm_from_factors(factors4, factors6), 12)

        # Factors of 15 (3*5) and 25 (5^2) -> LCM should be 75 (3 * 5^2)
        factors15 = collections.Counter({3:1, 5:1})
        factors25 = collections.Counter({5:2})
        self.assertEqual(calculate_lcm_from_factors(factors15, factors25), 75)

    def test_calculate_lcm_from_factors_multiple_of_other(self):
        # Factors of 5 (5^1) and 10 (2^1 * 5^1) -> LCM should be 10
        factors5 = collections.Counter({5: 1})
        factors10 = collections.Counter({2: 1, 5: 1})
        self.assertEqual(calculate_lcm_from_factors(factors5, factors10), 10)
        self.assertEqual(calculate_lcm_from_factors(factors10, factors5), 10) # Order shouldn't matter

    def test_calculate_lcm_from_factors_coprime(self):
        # Factors of 7 (7^1) and 5 (5^1) -> LCM should be 35
        factors7 = collections.Counter({7: 1})
        factors5 = collections.Counter({5: 1})
        self.assertEqual(calculate_lcm_from_factors(factors7, factors5), 35)

    def test_calculate_lcm_from_factors_one_number_is_one(self):
        factors1 = collections.Counter()
        factors_x = collections.Counter({2: 1, 3: 1}) # for 6
        self.assertEqual(calculate_lcm_from_factors(factors1, factors_x), 6)
        self.assertEqual(calculate_lcm_from_factors(factors_x, factors1), 6)

        factors_y = collections.Counter({7:1}) # for 7
        self.assertEqual(calculate_lcm_from_factors(factors1, factors_y), 7)

    def test_calculate_lcm_from_factors_both_numbers_are_one(self):
        factors1_a = collections.Counter()
        factors1_b = collections.Counter()
        self.assertEqual(calculate_lcm_from_factors(factors1_a, factors1_b), 1)

    # Tests for calculate_lcm(num1, num2)
    def test_calculate_lcm_basic(self):
        self.assertEqual(calculate_lcm(4, 6), 12)
        self.assertEqual(calculate_lcm(6, 4), 12)
        self.assertEqual(calculate_lcm(15, 25), 75)
        self.assertEqual(calculate_lcm(25, 15), 75)
        self.assertEqual(calculate_lcm(7, 5), 35)
        self.assertEqual(calculate_lcm(5, 7), 35)

    def test_calculate_lcm_one_input_is_one(self):
        self.assertEqual(calculate_lcm(1, 10), 10)
        self.assertEqual(calculate_lcm(10, 1), 10)
        self.assertEqual(calculate_lcm(1, 7), 7)
        self.assertEqual(calculate_lcm(1, 1), 1)

    def test_calculate_lcm_larger_numbers(self):
        self.assertEqual(calculate_lcm(24, 60), 120) # 24 = 2^3*3, 60 = 2^2*3*5. LCM = 2^3*3*5 = 120
        self.assertEqual(calculate_lcm(99, 88), 792) # 99 = 3^2*11, 88 = 2^3*11. LCM = 2^3*3^2*11 = 8*9*11 = 792

    def test_calculate_lcm_value_error(self):
        with self.assertRaises(ValueError):
            calculate_lcm(0, 5)
        with self.assertRaises(ValueError):
            calculate_lcm(5, 0)
        with self.assertRaises(ValueError):
            calculate_lcm(-2, 5)
        with self.assertRaises(ValueError):
            calculate_lcm(5, -2)
        with self.assertRaises(ValueError):
            calculate_lcm(0, 0)
        with self.assertRaises(ValueError):
            calculate_lcm(-5, -2)

if __name__ == '__main__':
    unittest.main()
