# -*- coding:utf-8 -*-

# ---
# 判断一个四则运算的括号是否匹配， 例如 3 * {3 +[(2 -3) * (4+5)]}
# 的括号是匹配的， 而 3 * {3+ [4 - 6}] 的括号是不匹配的。

# 思路使用stack实现


def judge_exp(expression):
	stack = []
	for i in expression:
		if i in '{[(':
			stack.append(i)
		elif i in ')]}':
			if len(stack) == 0:
				return False
			if i == '}':
				if stack[-1] == '{':
					stack.pop()
					if len(stack) == 0:
						return True
				else:
					return False
			elif i == ']':
				if stack[-1] == '[':
					stack.pop()
					if len(stack) == 0:
						return True
				else:
					return False
			elif i == ')':
				if stack[-1] == '(':
					stack.pop()
					if len(stack) == 0:
						return True
				else:
					return False

print judge_exp('3 * 3 +2 -3) * 4+5)]}'), '00000'
print judge_exp('3 * {3+ [4 - 6]}'), '1111111'


# 解析判断式优化  )(){}
def judge_exp_1(expression):
	stack = []
	brackets = (('{', '}'), ('[', ']'), ('(', ')'))
	for i in expression:
		if i in [t0[0] for t0 in brackets]:
			stack.append(i)
		elif i in [t1[1] for t1 in brackets]:
			if len(stack) == 0:
				print 'error'
				break
			left = stack.pop()
			bs = [t[1] for t in brackets if t[0] == left]
			if bs[0] != i:
				print 'error'
				break
	else:
		if len(stack) > 0:
			print 'error'
		else:
			print 'success'

# ---
# 给以c开头的字符串前面加上一个!，用最短的代码实现，列表解析
a = ['aaa', 'bbb', 'cc2c', 'ccc', 'dddd', 'c111']
a1 = tuple(a)
print a1
c = ['!' + x for x in a if x[0] == 'c'] + [x for x in a if x[0] != 'c']
c2 = ['!'+i for i in a if i.startswith('c')]
def p(x):
	if x.startswith('c'):
		return '!' + x
	return x
print map(p, a),'====='
print c
print c2
d1 = {'id': '111'}
# get
c3 = ['!{}'.format(x) if x[0] == 'c' else x+'#' for x in a]
c4 = []
print c3, '------'

# ---  TODO
# 不带括号的四则运算转化为前缀表达式。符号之间由空格分隔。
# 例如:
# 1 + 2 => + 1 2
# 1 + 2 * 3 => * 2 3 + 1


# -------〉4

# 分别使用递归、循环和生成器求菲波那切数列

def fibs_recursion(n):
	if n == 1:
		return 1
	if n == 2:
		return 1
	return fibs_recursion(n-1) + fibs_recursion(n-2)


def fibs_circle(n):
	if n == 1:
		return 1
	ae = 1
	b = 0
	for t in range(n):
		ae, b = b, a + b
	return b


def fibs_gen(n):
	if n == 1:
		yield 1
	ae = 1
	b = 0
	for t in range(n):
		ae, b = b, ae + b
		yield b


def fibs_generator():
	idx = 0
	a3, b = 1, 1
	while True:
		if idx == 0 or idx == 1:
			yield 1
		else:
			a3, b = b, a3+b
			yield b
		idx += 1


def fibs4(n):
	gen = fibs_generator()
	for _ in range(n+1):
		print next(gen)

# 写一个函数，实现对整数的排序，默认升序排列。 不能使用任何内置函数和第三方库。
# 插入排序
# 354929031，不考虑空间复杂度的算法，考虑空间复杂度的算法


def insert_sort(lst, reverse=False):
	if len(lst) == 0:
		raise Exception('it is empty')
	dst = []
	for n in lst:
		for idx, e in enumerate(dst):
			if not reverse:
				if n < e:
					dst.insert(idx, n)
					break
			else:
				if n > e:
					dst.insert(idx, n)
					break
		else:
			dst.append(n)
	print dst, '=========='


# 写一个函数，把罗马数字转化为整数。输入为 1 到 3999之间的任意数字


def roma2int(num):
	pass

# 写一个函数，求两个字符串的最长公共子串。
# 例如 输入 I love Python 和 Python is a simple language， 输出为Python
