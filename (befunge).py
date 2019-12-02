#!/usr/bin/env python3

import os
import sys
from dataclasses import dataclass
import itertools
import string

DEBUG = 'DEBUG' in os.environ

@dataclass
class PC:
    row: int
    col: int
    direction: str
    str_mode: bool
    def step(self):
        if self.direction == '>':
            self.col += 1
        elif self.direction == 'v':
            self.row += 1
        elif self.direction == '<':
            self.col -= 1
        elif self.direction == '^':
            self.row -= 1
        self.row %= 25
        self.col %= 80

class Stack:
    def __init__(self):
        self.s = []
    def pop(self, n=None):
        if n:
            return [self.pop() for _ in range(n)][::-1]
        return self.s.pop() if self.s else 0
    def push(self, val):
        self.s.append(val)

printable = string.ascii_letters + string.digits + string.punctuation + ' '
def print_state(pc, stack, prog):
    print('pc:', pc)
    print('stack:', stack.s)
    xs = []
    for row, chs in enumerate(prog):
        for col, ch in enumerate(chs):
            if row == pc.row and col == pc.col:
                print('\u001b[44m\u001b[37;1m', end='')
            if isinstance(ch, int):
                print('X', end='')
                xs.append((row, col, ch))
            else:
                print(ch, end='')
            print('\u001b[0m', end='')
        print()
    for row, col, x in xs:
        print(f'({row},{col}): {x}')

if __name__ == '__main__':
    prog = [[' ' for _ in range(80)] for _ in range(25)]
    with open(sys.argv[1], 'r') as f:
        for row, line in enumerate(itertools.islice(f, 25)):
            for col, ch in enumerate(itertools.islice(line.rstrip('\n'), 80)):
                prog[row][col] = ch
    pc = PC(row=0, col=0, direction='>', str_mode=False)
    stack = Stack()
    stdin = iter(open(sys.argv[2], 'r'))
    while True:
        ins = prog[pc.row][pc.col]
        if DEBUG:
            print_state(pc, stack, prog)
            print('> ', end='')
            cmd = input().split()
        if ins == '"':
            pc.str_mode = not pc.str_mode
        elif pc.str_mode:
            stack.push(ord(ins))
        elif ins in [str(x) for x in range(10)]:
            stack.push(int(ins))
        elif ins == '+':
            stack.push(stack.pop() + stack.pop())
        elif ins == '-':
            a, b = stack.pop(2)
            stack.push(a-b)
        elif ins == '/':
            a, b = stack.pop(2)
            stack.push(a//b)
        elif ins == '$':
            stack.pop()
        elif ins in ('>','v','<','^'):
            pc.direction = ins
        elif ins == ':':
            val = stack.pop()
            stack.push(val)
            stack.push(val)
        elif ins == '#':
            pc.step()
        elif ins == ',':
            print(chr(stack.pop()), end='')
        elif ins == '.':
            print(stack.pop())
        elif ins == 'p':
            val, col, row = stack.pop(3)
            prog[row][col] = val
        elif ins == 'g':
            col, row = stack.pop(2)
            stack.push(prog[row][col])
        elif ins == '`':
            a, b = stack.pop(2)
            stack.push(1 if a > b else 0)
        elif ins == '_':
            if stack.pop():
                pc.direction = '<'
            else:
                pc.direction = '>'
        elif ins == '&':
            try:
                val = int(next(stdin))
            except StopIteration:
                val = -1
            stack.push(val)
        elif ins == '!':
            stack.push(0 if stack.pop() else 1)
        elif ins == '@':
            break
        elif ins == ' ':
            pass
        else:
            raise ValueError('unknown instruction: '+ins)
        pc.step()
