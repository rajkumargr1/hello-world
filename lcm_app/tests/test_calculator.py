import unittest
import collections

# Adjust import path if necessary.
try:
    from lcm_app.calculator import get_prime_factorization, calculate_lcm_from_factors, calculate_lcm
except ImportError:
    from calculator import get_prime_factorization, calculate_lcm_from_factors, calculate_lcm


class TestCalculator(unittest.TestCase):

    # Tests for get_prime_factorization(n) - Should remain largely unchanged but ensure comprehensive
    def test_get_prime_factorization_prime(self):
        self.assertEqual(get_prime_factorization(7), collections.Counter({7: 1}))
        self.assertEqual(get_prime_factorization(2), collections.Counter({2: 1}))
        self.assertEqual(get_prime_factorization(13), collections.Counter({13: 1}))

    def test_get_prime_factorization_composite(self):
        self.assertEqual(get_prime_factorization(12), collections.Counter({2: 2, 3: 1}))
        self.assertEqual(get_prime_factorization(30), collections.Counter({2: 1, 3: 1, 5: 1}))
        self.assertEqual(get_prime_factorization(100), collections.Counter({2: 2, 5: 2}))

    def test_get_prime_factorization_power_of_prime(self):
        self.assertEqual(get_prime_factorization(8), collections.Counter({2: 3}))
        self.assertEqual(get_prime_factorization(27), collections.Counter({3: 3}))

    def test_get_prime_factorization_one(self):
        self.assertEqual(get_prime_factorization(1), collections.Counter())

    def test_get_prime_factorization_large_number(self):
        self.assertEqual(get_prime_factorization(99), collections.Counter({3: 2, 11: 1}))
        self.assertEqual(get_prime_factorization(77), collections.Counter({7:1, 11:1})) # Test optimization

    def test_get_prime_factorization_value_error(self):
        with self.assertRaises(ValueError):
            get_prime_factorization(0)
        with self.assertRaises(ValueError):
            get_prime_factorization(-5)

    # Tests for calculate_lcm_from_factors(factor_counters_list)
    def test_calculate_lcm_from_factors_two_counters(self):
        factors4 = collections.Counter({2: 2})
        factors6 = collections.Counter({2: 1, 3: 1})
        self.assertEqual(calculate_lcm_from_factors([factors4, factors6]), 12)

        factors15 = collections.Counter({3:1, 5:1})
        factors25 = collections.Counter({5:2})
        self.assertEqual(calculate_lcm_from_factors([factors15, factors25]), 75)

    def test_calculate_lcm_from_factors_multiple_counters(self):
        f2 = get_prime_factorization(2) # Counter({2:1})
        f3 = get_prime_factorization(3) # Counter({3:1})
        f4 = get_prime_factorization(4) # Counter({2:2})
        # LCM(2,3,4) = 12
        self.assertEqual(calculate_lcm_from_factors([f2, f3, f4]), 12)

        f6 = get_prime_factorization(6)   # Counter({2:1, 3:1})
        f8 = get_prime_factorization(8)   # Counter({2:3})
        f12 = get_prime_factorization(12) # Counter({2:2, 3:1})
        # LCM(6,8,12) = 24
        self.assertEqual(calculate_lcm_from_factors([f6, f8, f12]), 24)

        f1 = get_prime_factorization(1)
        f5 = get_prime_factorization(5)
        f7 = get_prime_factorization(7)
        f10 = get_prime_factorization(10) # 2:1, 5:1
        # LCM(1,5,7,10) = 70
        self.assertEqual(calculate_lcm_from_factors([f1, f5, f7, f10]), 70)


    def test_calculate_lcm_from_factors_empty_list(self):
        self.assertEqual(calculate_lcm_from_factors([]), 1)

    def test_calculate_lcm_from_factors_single_counter(self):
        factors7 = collections.Counter({7: 1})
        self.assertEqual(calculate_lcm_from_factors([factors7]), 7)

        factors12 = collections.Counter({2:2, 3:1})
        self.assertEqual(calculate_lcm_from_factors([factors12]), 12)

        factors1 = collections.Counter()
        self.assertEqual(calculate_lcm_from_factors([factors1]), 1) # LCM of factors of 1 is 1

    def test_calculate_lcm_from_factors_with_one_as_factor(self):
        factors1 = collections.Counter()
        factors_x = collections.Counter({2: 1, 3: 1}) # for 6
        self.assertEqual(calculate_lcm_from_factors([factors1, factors_x]), 6)
        self.assertEqual(calculate_lcm_from_factors([factors_x, factors1]), 6)

    # Tests for calculate_lcm(*numbers)
    def test_calculate_lcm_two_numbers(self): # Keep existing two-number tests
        self.assertEqual(calculate_lcm(4, 6), 12)
        self.assertEqual(calculate_lcm(15, 25), 75)
        self.assertEqual(calculate_lcm(7, 5), 35)
        self.assertEqual(calculate_lcm(1, 10), 10)
        self.assertEqual(calculate_lcm(10, 1), 10)
        self.assertEqual(calculate_lcm(1, 1), 1)

    def test_calculate_lcm_multiple_numbers(self):
        self.assertEqual(calculate_lcm(2, 3, 4), 12)
        self.assertEqual(calculate_lcm(6, 8, 12), 24)
        self.assertEqual(calculate_lcm(1, 2, 3, 4, 5), 60)
        # 7=7, 14=2*7, 21=3*7, 28=2^2*7. LCM = 2^2 * 3 * 7 = 4 * 3 * 7 = 12 * 7 = 84
        self.assertEqual(calculate_lcm(7, 14, 21, 28), 84)
        self.assertEqual(calculate_lcm(10, 20, 30, 40), 120) # From calculator.py main

    def test_calculate_lcm_single_argument(self):
        self.assertEqual(calculate_lcm(10), 10)
        self.assertEqual(calculate_lcm(7), 7)
        self.assertEqual(calculate_lcm(1), 1)

    def test_calculate_lcm_value_error_no_args(self):
        with self.assertRaisesRegex(ValueError, "At least one number must be provided"):
            calculate_lcm()

    def test_calculate_lcm_value_error_non_positive_multi_args(self):
        with self.assertRaisesRegex(ValueError, "All inputs must be positive integers."):
            calculate_lcm(2, 0, 3)
        with self.assertRaisesRegex(ValueError, "All inputs must be positive integers."):
            calculate_lcm(2, 3, -4)
        with self.assertRaisesRegex(ValueError, "All inputs must be positive integers."):
            calculate_lcm(0, 0, 0)
        with self.assertRaisesRegex(ValueError, "All inputs must be positive integers."):
            calculate_lcm(1, 2, 0) # Test with zero at the end

    def test_calculate_lcm_value_error_non_positive_single_arg(self): # Retest from original
        with self.assertRaises(ValueError):
            calculate_lcm(0)
        with self.assertRaises(ValueError):
            calculate_lcm(-5)

    def test_calculate_lcm_duplicate_numbers(self):
        self.assertEqual(calculate_lcm(4, 6, 4), 12)
        self.assertEqual(calculate_lcm(5, 5, 5), 5)

    def test_calculate_lcm_order_invariance(self):
        self.assertEqual(calculate_lcm(2,3,4), calculate_lcm(4,3,2))
        self.assertEqual(calculate_lcm(12,8,6), calculate_lcm(6,8,12))


if __name__ == '__main__':
    unittest.main()
