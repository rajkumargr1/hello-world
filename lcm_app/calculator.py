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
    if temp_n > 1: # Remaining n must be a prime factor
        factors[temp_n] += 1
    return factors

def calculate_lcm_from_factors(num1_factors: collections.Counter, num2_factors: collections.Counter) -> int:
    """
    Calculates the Least Common Multiple (LCM) from the prime factorizations of two numbers.

    Args:
        num1_factors: Prime factorization of the first number (collections.Counter).
        num2_factors: Prime factorization of the second number (collections.Counter).

    Returns:
        The LCM as an integer.
    """
    if not num1_factors: # Handles case where first number is 1
        lcm = 1
        for factor, power in num2_factors.items():
            lcm *= factor ** power
        return lcm if lcm !=0 else 1 # if num2 is also 1, lcm is 1

    if not num2_factors: # Handles case where second number is 1
        lcm = 1
        for factor, power in num1_factors.items():
            lcm *= factor ** power
        return lcm if lcm !=0 else 1 # if num1 is also 1, lcm is 1

    # Combine factors: for each prime, take the maximum power.
    all_primes = set(num1_factors.keys()) | set(num2_factors.keys())
    lcm = 1
    for prime in all_primes:
        power1 = num1_factors.get(prime, 0)
        power2 = num2_factors.get(prime, 0)
        lcm *= prime ** max(power1, power2)

    return lcm

def calculate_lcm(num1: int, num2: int) -> int:
    """
    Calculates the Least Common Multiple (LCM) of two positive integers.

    Args:
        num1: The first positive integer.
        num2: The second positive integer.

    Returns:
        The LCM of num1 and num2.

    Raises:
        ValueError: If either num1 or num2 is less than 1.
    """
    if num1 < 1 or num2 < 1:
        raise ValueError("Inputs must be positive integers.")

    if num1 == 1: return num2
    if num2 == 1: return num1

    # A more direct way to calculate LCM if GCD is available: (num1 * num2) // gcd(num1, num2)
    # However, the requirement is to use prime factorization.

    factors1 = get_prime_factorization(num1)
    factors2 = get_prime_factorization(num2)

    return calculate_lcm_from_factors(factors1, factors2)

if __name__ == '__main__':
    # Example Usage:
    print(f"Prime factorization of 12: {get_prime_factorization(12)}")
    print(f"Prime factorization of 18: {get_prime_factorization(18)}")

    factors_12 = get_prime_factorization(12) # {2: 2, 3: 1}
    factors_18 = get_prime_factorization(18) # {2: 1, 3: 2}
    lcm_12_18 = calculate_lcm_from_factors(factors_12, factors_18)
    print(f"LCM of 12 and 18 (from factors): {lcm_12_18}") # Expected: 36

    print(f"LCM of 12 and 18 (direct): {calculate_lcm(12, 18)}")
    print(f"LCM of 7 and 5: {calculate_lcm(7, 5)}") # Expected: 35
    print(f"LCM of 1 and 5: {calculate_lcm(1, 5)}") # Expected: 5
    print(f"LCM of 15 and 25: {calculate_lcm(15, 25)}") # Expected: 75

    try:
        get_prime_factorization(0)
    except ValueError as e:
        print(f"Error for get_prime_factorization(0): {e}")

    try:
        calculate_lcm(0, 5)
    except ValueError as e:
        print(f"Error for calculate_lcm(0, 5): {e}")

    print(f"Prime factorization of 1: {get_prime_factorization(1)}")
    print(f"LCM of 1 and 1: {calculate_lcm(1,1)}") # Expected: 1
    print(f"LCM of 1 and 7: {calculate_lcm(1,7)}") # Expected: 7
    print(f"LCM of 60 and 24: {calculate_lcm(60, 24)}") # Expected: 120
    # 60 = 2^2 * 3 * 5
    # 24 = 2^3 * 3
    # LCM = 2^3 * 3 * 5 = 8 * 3 * 5 = 120
    print(f"Prime factorization of 60: {get_prime_factorization(60)}")
    print(f"Prime factorization of 24: {get_prime_factorization(24)}")

    print(f"Prime factorization of 2: {get_prime_factorization(2)}")
    print(f"Prime factorization of 3: {get_prime_factorization(3)}")
    print(f"LCM of 2 and 3: {calculate_lcm(2,3)}")

    print(f"Prime factorization of 999999937 (prime): {get_prime_factorization(999999937)}")
    print(f"LCM of 999999937 and 2: {calculate_lcm(999999937, 2)}")
