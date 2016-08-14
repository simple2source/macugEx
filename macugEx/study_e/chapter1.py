# -*- coding:utf-8 -*-
import math

# 1
in_number = 33
i = 0
while i < 3:
    # guess_number = int(raw_input("please input int number:"))
    guess_number = 33
    if guess_number == in_number:
        print("congratulations！ you win!")
        break
    i += 1
    if i == 3:
        print("Oops! you fail!")

# 2
lst = [1, 3, 2, 4, 3, 4, 5, 5, 7]
s1 = list(set(lst))
s1.sort(key=lst.index)
print s1

# 3,判断素数


def is_prime(n):
    if n == 2:
        return True
    if n % 2 == 0 or n <= 1:
        return False

    sqr = int(math.sqrt(n)) + 1

    for divisor in range(3, sqr, 2):
        if n % divisor == 0:
            return False
    return True


def count_prime(lst):
    count = 0
    for i in lst:
        if is_prime(i):
            count += 1
    print count
    return count


def prime_test(lst):
    count = 0
    for i in lst:
        if i < 2:
            pass
        elif i == 2:
            count += 1
        elif i % 2 == 0:
            pass
        else:
            sqr = int(math.sqrt(i)) + 1
            for x in range(3, sqr, 2):
                if i % x == 0:
                    break
            else:
                count += 1
    print count
    return count

count_prime([2,3,4,7,8,11,55,77,7])
prime_test([2,3,4,7,8,11,55,77,7])


# google 上找到的一个求素数的算法 https://inventwithpython.com/hacking/chapter23.html

def primeSieve(sieveSize):
    # Returns a list of prime numbers calculated using
    # the Sieve of Eratosthenes algorithm.
    sieve = [True] * sieveSize
    sieve[0] = False  # zero and one are not prime numbers
    sieve[1] = False
    # create the sieve
    for i in range(2, int(math.sqrt(sieveSize))+1):
         pointer = i * 2
         while pointer < sieveSize:
             sieve[pointer] = False
             pointer += i
    primes = []
    for i in range(sieveSize):
        if sieve[i] == True:
            primes.append(i)
    print primes
    return primes
primeSieve(100)

print math.factorial(5)

# 杨辉三角


def print_pascal(line):
    results = []
    for _ in range(line):
        row = [1]
        if results:
            last_row = results[-1]
            row.extend(sum(pair) for pair in zip(last_row,  last_row[1:]))
            row.append(1)
            print last_row,last_row[1:]
        results.append(row)
    return results

for x in print_pascal(10):
    print x


