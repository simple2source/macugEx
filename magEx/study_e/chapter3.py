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

# ---
# 不带括号的四则运算转化为前缀表达式。符号之间由空格分隔。
# 例如:
# 1 + 2 => + 1 2
# 1 + 2 * 3 => * 2 3 + 1
