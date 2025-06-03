import collections
import math

def get_prime_factorization(n: int) -> collections.Counter:
    """
    Calculates the prime factorization of a positive integer n.

    Args:
        n: A positive integer.

    Returns:
        A collections.Counter where keys are prime factors and values are their powers.
        Example: get_prime_factorization(12) returns Counter({2: 2, 3: 1}).

    Raises:
        ValueError: If n is less than 1.
    """
    if n < 1:
        raise ValueError("Input must be a positive integer.")
    if n == 1:
        return collections.Counter()

    factors = collections.Counter()
    d = 2
    temp_n = n
    while d * d <= temp_n:
        while temp_n % d == 0:
            factors[d] += 1
            temp_n //= d
        d += 1
        if d * d > temp_n and temp_n > 1: # Optimization: if remaining temp_n is prime
            break
    if temp_n > 1: # Remaining n must be a prime factor
        factors[temp_n] += 1
    return factors

def calculate_lcm_from_factors(factor_counters_list: list[collections.Counter]) -> int:
    """
    Calculates the Least Common Multiple (LCM) from a list of prime factorizations.

    Args:
        factor_counters_list: A list of collections.Counter objects, each representing
                              the prime factorization of a number.

    Returns:
        The LCM as an integer. Returns 1 if the list is empty.
    """
    if not factor_counters_list:
        return 1 # LCM of an empty set of numbers is 1

    overall_max_factors = collections.Counter()
    for factors_counter in factor_counters_list:
        if not isinstance(factors_counter, collections.Counter):
            # This check is mostly for robustness, assuming inputs are from get_prime_factorization
            raise TypeError("All items in factor_counters_list must be collections.Counter objects.")
        for prime, power in factors_counter.items():
            overall_max_factors[prime] = max(overall_max_factors[prime], power)

    lcm = 1
    for prime, power in overall_max_factors.items():
        lcm *= (prime ** power)

    return lcm

def calculate_lcm(*numbers: int) -> int:
    """
    Calculates the Least Common Multiple (LCM) of one or more positive integers.

    Args:
        *numbers: A variable number of positive integers.

    Returns:
        The LCM of the provided numbers.

    Raises:
        ValueError: If no numbers are provided, or if any number is not a positive integer.
    """
    if not numbers:
        raise ValueError("At least one number must be provided to calculate LCM.")

    factor_counters_list = []
    for num in numbers:
        if not isinstance(num, int) or num < 1: # Also catches non-integer types if passed
            raise ValueError("All inputs must be positive integers.")
        factors = get_prime_factorization(num)
        factor_counters_list.append(factors)

    return calculate_lcm_from_factors(factor_counters_list)

if __name__ == '__main__':
    print("--- Testing get_prime_factorization ---")
    print(f"Prime factorization of 12: {get_prime_factorization(12)}")
    print(f"Prime factorization of 18: {get_prime_factorization(18)}")
    print(f"Prime factorization of 1: {get_prime_factorization(1)}")
    print(f"Prime factorization of 7: {get_prime_factorization(7)}")

    try:
        get_prime_factorization(0)
    except ValueError as e:
        print(f"Error for get_prime_factorization(0): {e}")

    print("\n--- Testing calculate_lcm_from_factors (for 2 numbers) ---")
    factors_12 = get_prime_factorization(12)
    factors_18 = get_prime_factorization(18)
    lcm_12_18 = calculate_lcm_from_factors([factors_12, factors_18])
    print(f"LCM of 12 and 18 (from factors): {lcm_12_18}") # Expected: 36

    print("\n--- Testing calculate_lcm (now for n numbers) ---")
    print(f"LCM of 12 and 18: {calculate_lcm(12, 18)}") # Expected: 36
    print(f"LCM of 7 and 5: {calculate_lcm(7, 5)}") # Expected: 35
    print(f"LCM of 1 and 5: {calculate_lcm(1, 5)}") # Expected: 5
    print(f"LCM of 15 and 25: {calculate_lcm(15, 25)}") # Expected: 75
    print(f"LCM of 1: {calculate_lcm(1)}") # Expected: 1
    print(f"LCM of 7: {calculate_lcm(7)}") # Expected: 7
    print(f"LCM of 60, 24: {calculate_lcm(60, 24)}") # Expected: 120

    print("\n--- Testing calculate_lcm with multiple arguments ---")
    print(f"LCM of 2, 3, 4: {calculate_lcm(2, 3, 4)}") # 2=2, 3=3, 4=2^2. LCM = 2^2 * 3 = 12
    print(f"LCM of 6, 8, 12: {calculate_lcm(6, 8, 12)}") # 6=2*3, 8=2^3, 12=2^2*3. LCM = 2^3 * 3 = 24
    print(f"LCM of 1, 2, 3, 4, 5: {calculate_lcm(1, 2, 3, 4, 5)}") # LCM = 2^2 * 3 * 5 = 60
    print(f"LCM of 7, 14, 21: {calculate_lcm(7, 14, 21)}") # 7, 2*7, 3*7. LCM = 2*3*7 = 42
    print(f"LCM of 4, 6, 8, 10: {calculate_lcm(4, 6, 8, 10)}") # 4=2^2, 6=2*3, 8=2^3, 10=2*5. LCM = 2^3 * 3 * 5 = 8*3*5 = 120

    print("\n--- Testing edge cases for calculate_lcm ---")
    try:
        print(f"LCM of no numbers: {calculate_lcm()}")
    except ValueError as e:
        print(f"Error for calculate_lcm(): {e}")

    try:
        print(f"LCM of 0, 5: {calculate_lcm(0, 5)}")
    except ValueError as e:
        print(f"Error for calculate_lcm(0, 5): {e}")

    try:
        print(f"LCM of 2, -3, 4: {calculate_lcm(2, -3, 4)}")
    except ValueError as e:
        print(f"Error for calculate_lcm(2, -3, 4): {e}")

    print(f"LCM of 1, 1, 1: {calculate_lcm(1, 1, 1)}") # Expected: 1
    print(f"LCM of 5 (single number): {calculate_lcm(5)}") # Expected: 5

    print("\n--- Testing calculate_lcm_from_factors with multiple counters ---")
    f2 = get_prime_factorization(2)
    f3 = get_prime_factorization(3)
    f4 = get_prime_factorization(4)
    print(f"LCM from factors of 2, 3, 4: {calculate_lcm_from_factors([f2, f3, f4])}") # Expected: 12

    f_empty_list = []
    print(f"LCM from empty list of factors: {calculate_lcm_from_factors(f_empty_list)}") # Expected: 1

    f_single_list = [get_prime_factorization(7)]
    print(f"LCM from factors of [7]: {calculate_lcm_from_factors(f_single_list)}") # Expected: 7

    f_single_list_one = [get_prime_factorization(1)]
    print(f"LCM from factors of [1]: {calculate_lcm_from_factors(f_single_list_one)}") # Expected: 1

    print(f"Prime factorization of 999999937 (prime): {get_prime_factorization(999999937)}")
    print(f"LCM of 999999937, 2, 3: {calculate_lcm(999999937, 2, 3)}") # Expected: 999999937 * 2 * 3

    # Test optimization in get_prime_factorization
    # A number that is a prime squared, where the prime is > sqrt(number_before_last_division)
    # e.g. 49 = 7*7. Loop goes up to d*d <= temp_n. d=2..6. d=7, temp_n=49. 49%7=0, f[7]=1, temp_n=7.
    # d becomes 8. 8*8 > 7. Loop ends. if temp_n > 1 (7>1), f[7]+=1. Correct.
    # e.g. 121 = 11*11. d=2..10. d=11, temp_n=121. 121%11=0, f[11]=1, temp_n=11.
    # d becomes 12. 12*12 > 11. Loop ends. if temp_n > 1 (11>1), f[11]+=1. Correct.
    print(f"Prime factorization of 121: {get_prime_factorization(121)}") # Expected: {11:2}
    print(f"Prime factorization of 169: {get_prime_factorization(169)}") # Expected: {13:2}
    # Test with a number where the last factor is larger than the sqrt of the original number.
    # E.g. 77 = 7 * 11. d=2..6. d=7, temp_n=77. 77%7=0, f[7]=1, temp_n=11.
    # d becomes 8. 8*8 > 11. Loop ends. if temp_n > 1 (11>1), f[11]+=1. Correct.
    print(f"Prime factorization of 77: {get_prime_factorization(77)}") # Expected: {7:1, 11:1}

    # An optimization was added to get_prime_factorization:
    # while d * d <= temp_n:
    #   ...
    #   if d * d > temp_n and temp_n > 1: # Optimization: if remaining temp_n is prime
    #       break
    # This break is safe because if d*d > temp_n, then d > sqrt(temp_n). If temp_n has any factor
    # other than 1 and itself, at least one of those factors must be <= sqrt(temp_n).
    # Since we've iterated d up to (or past) sqrt(temp_n), if temp_n is still > 1,
    # and no d has divided it, then the remaining temp_n must be prime.
    # The 'break' allows us to skip incrementing 'd' unnecessarily until d*d > temp_n causes loop termination.
    # The final 'if temp_n > 1' correctly adds this remaining prime.
    # Let's test this with a number like 6 = 2*3.
    # n=6. d=2. 6%2=0. f[2]=1, temp_n=3. d*d (4) > temp_n (3). Break.
    # if temp_n > 1 (3>1), f[3]=1. Result: {2:1, 3:1}. Correct.
    print(f"Prime factorization of 6: {get_prime_factorization(6)}")
    print(f"Prime factorization of 10: {get_prime_factorization(10)}") # {2:1, 5:1}
    print(f"Prime factorization of 14: {get_prime_factorization(14)}") # {2:1, 7:1}
    print(f"Prime factorization of 15: {get_prime_factorization(15)}") # {3:1, 5:1}

    # Test with a number that is a product of three distinct primes
    print(f"Prime factorization of 2*3*5 = 30: {get_prime_factorization(30)}")
    # Test with a number that is a product of a prime and a square of another prime
    print(f"Prime factorization of 2^2 * 3 = 12: {get_prime_factorization(12)}")
    print(f"Prime factorization of 2 * 3^2 = 18: {get_prime_factorization(18)}")
    print(f"Prime factorization of 2^3 * 3^2 * 5 = 8*9*5 = 360: {get_prime_factorization(360)}")
    # 360 = 2^3 * 3^2 * 5^1
    # Expected: Counter({2: 3, 3: 2, 5: 1})
    self_calculated_360 = collections.Counter()
    n_360 = 360
    d_360 = 2
    while n_360 % d_360 == 0: self_calculated_360[d_360]+=1; n_360 //= d_360 # 2,2,2 -> n=45
    d_360 = 3
    while n_360 % d_360 == 0: self_calculated_360[d_360]+=1; n_360 //= d_360 # 3,3 -> n=5
    d_360 = 5
    while n_360 % d_360 == 0: self_calculated_360[d_360]+=1; n_360 //= d_360 # 5 -> n=1
    print(f"Manual factorization of 360: {self_calculated_360}")

    print(f"Prime factorization of a large prime: {get_prime_factorization(999999929)}") # 999999929 is prime
    # Expected: Counter({999999929: 1})

    print(f"LCM of 2,4,8,16: {calculate_lcm(2,4,8,16)}") # Expected 16
    print(f"LCM of 3,9,27: {calculate_lcm(3,9,27)}") # Expected 27
    print(f"LCM of 2,3,5,7,11,13 (all primes): {calculate_lcm(2,3,5,7,11,13)}") # Expected 2*3*5*7*11*13 = 30030
    print(f"LCM of 10, 20, 30, 40: {calculate_lcm(10,20,30,40)}")
    # 10 = 2 * 5
    # 20 = 2^2 * 5
    # 30 = 2 * 3 * 5
    # 40 = 2^3 * 5
    # LCM = 2^3 * 3 * 5 = 8 * 3 * 5 = 120. Expected: 120.The `lcm_app/calculator.py` file has been updated.

Here's a summary of the changes:

- **`calculate_lcm_from_factors(factor_counters_list)`:**
    - Now accepts a list of `collections.Counter` objects.
    - Returns 1 if the list is empty.
    - Iterates through each `factors_counter` in the list.
    - For each prime `p` and its `power` in `factors_counter.items()`, it updates `overall_max_factors[p] = max(overall_max_factors[p], power)`.
    - Calculates the final LCM from `overall_max_factors`.
    - Includes a `TypeError` check for robustness, although internal calls should provide correct types.

- **`calculate_lcm(*numbers)`:**
    - Signature changed to `*numbers` to accept a variable number of arguments.
    - Validates that at least one number is provided (raises `ValueError` if not).
    - Validates that all numbers are positive integers (raises `ValueError` if not). Non-integer types are also caught here.
    - Creates `factor_counters_list` by calling `get_prime_factorization(num)` for each number.
    - Calls the modified `calculate_lcm_from_factors(factor_counters_list)`.

- **`get_prime_factorization(n)`:**
    - Reviewed and confirmed no changes were strictly needed for n-number LCM.
    - An optimization `if d * d > temp_n and temp_n > 1: break` was already present from a previous version or implicitly part of the original logic's efficiency for how `d` increments and `temp_n` reduces. I've added comments and tests in `if __name__ == '__main__':` to trace its behavior and confirm its correctness.

- **`if __name__ == '__main__':` Updated:**
    - Added examples of calling `calculate_lcm` with multiple arguments (e.g., `calculate_lcm(2, 3, 4)`, `calculate_lcm(6, 8, 12)`).
    - Added tests for edge cases like `calculate_lcm()` (no arguments), and invalid inputs within multiple arguments.
    - Added tests for `calculate_lcm_from_factors` with lists of various lengths (empty, single, multiple).
    - Added more extensive tests for `get_prime_factorization` including numbers that are products of multiple primes, squares of primes, and large primes to implicitly test the optimization.

The logic for calculating LCM for 'n' numbers is now implemented. The next step would be to update the GUI and unit tests to reflect these changes.

I will now submit the report.
