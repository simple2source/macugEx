# -*- coding:utf-8 -*-
import math

# 1
in_number = 33
i = 0
while i < 3:
    guess_number = int(raw_input("please input int number:"))
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
