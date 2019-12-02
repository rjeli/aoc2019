#!/usr/bin/env python3
"""
Usage:
    ./(befunge).py <prog> <input> [--video]
"""

import os
import sys
from dataclasses import dataclass
import itertools
import string
from docopt import docopt
import collections

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
printable_ords = [ord(ch) for ch in printable]
def print_state(pc, stack, prog, bp, ret_img):
    font_h, font_w = 22, 14
    if ret_img:
        from wand.color import Color
        from wand.image import Image
        from wand.drawing import Drawing
        draw = Drawing()
        draw.__enter__()
        img = Image(width=font_w*80, height=font_h*25, 
            background=Color('#fdf6e3'))
        img.__enter__()
        font_path = '/Applications/Utilities/Terminal.app/Contents'
        font_path += '/Resources/Fonts/SFMono-Regular.otf' 
        draw.font = font_path
        draw.font_size = font_h
        draw.text(0, font_h, 'hello world!!')
    import os; os.system('clear')
    def p(*args, **kwargs):
        kwargs.update(flush=False)
        print(*args, **kwargs)
    p('pc:', pc)
    p('stack:', stack.s)
    ptr = None
    if prog[pc.row][pc.col] in (ord('p'), ord('g')):
        ptr = (stack.s[-1], stack.s[-2])
    xs = {}
    for row, chs in enumerate(prog):
        for col, ch in enumerate(chs):
            if ret_img:
                draw.fill_color = Color('#073642')
            if bp and (row,col) == bp:
                p('\u001b[42m\u001b[37;1m', end='')
            if (row,col) == (pc.row,pc.col):
                p('\u001b[44m\u001b[37;1m', end='')
                if ret_img:
                    draw.push()
                    draw.fill_color = Color('#d33682')
                    draw.rectangle(
                        font_w*col,font_h*row+font_h//10,
                        font_w*(col+1)-1,font_h*(row+1)+font_h//10)
                    draw.pop()
                    draw.fill_color = Color('#fdf6e3')
            if ptr and (row,col) == ptr:
                p('\u001b[46m\u001b[37;1m', end='')
            if ch in printable_ords:
                p(chr(ch), end='')
                if ret_img:
                    draw.text(font_w*col, font_h*(row+1), chr(ch))
            else:
                p('X', end='')
                xs[(row,col)] = ch
            p('\u001b[0m', end='')
        p()
    print(end='', flush=True)
    """
    rows = set(r for r, c in xs)
    cols = set(c for r, c in xs)
    widths = {}
    print('   ', end='')
    for col in sorted(list(cols)):
        col_xs = [xs[r,c] for r, c in xs if c == col]
        widest = max(len(str(x)) for x in col_xs+[col])
        widths[col] = widest
        w = len(str(col))
        print(' '*(1+widest-w), end='')
        print(col, end='')
    print()
    for row in sorted(list(rows)):
        print(' '*(2-len(str(row))), end='')
        print(row, end='')
        print(':', end='')
        for col in sorted(list(cols)):
            if (row,col) in xs:
                x = xs[(row,col)]
                w = len(str(x))
                print(' '*(1+widths[col]-w), end='')
                if ptr and (row,col) == ptr:
                    print('\u001b[46m\u001b[37;1m', end='')
                print(x, end='')
                print('\u001b[0m', end='')
            else:
                print(' '*(1+widths[col]), end='')
        print()
    if ret_img:
        draw(img)
        img.save(filename='draw.png')
        img.__exit__(None, None, None)
        draw.__exit__(None, None, None)
    """

if __name__ == '__main__':
    args = docopt(__doc__)
    prog = [[ord(' ') for _ in range(80)] for _ in range(25)]
    with open(args['<prog>'], 'r') as f:
        for row, line in enumerate(itertools.islice(f, 25)):
            for col, ch in enumerate(itertools.islice(line.rstrip('\n'), 80)):
                prog[row][col] = ord(ch)
    pc = PC(row=0, col=0, direction='>', str_mode=False)
    stack = Stack()
    stdin = iter(open(args['<input>'], 'r'))
    bp = None
    cont = False
    while True:
        ins = chr(prog[pc.row][pc.col])
        hit_bp = bp == (pc.row, pc.col)
        if 'PLAY' in os.environ and ins != ' ':
            print_state(pc, stack, prog, bp, False)
            import time; time.sleep(0.005)
        elif DEBUG and ((not cont and ins != ' ') or hit_bp):
            while True:
                print_state(pc, stack, prog, bp, args['--video'])
                print('> ', end='')
                cmd = input().rstrip().split() or ['n']
                cont = False
                if cmd[0] == 'b':
                    if bp is None:
                        bp = (int(cmd[1]), int(cmd[2]))
                        print('set bp at', bp)
                    else:
                        bp = None
                        print('removed bp')
                elif cmd[0] == 'c':
                    cont = True
                    break
                elif cmd[0] == 'n':
                    break
                else:
                    print('unknown cmd:', cmd)
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
        elif ins == '*':
            a, b = stack.pop(2)
            stack.push(a*b)
        elif ins == '/':
            a, b = stack.pop(2)
            stack.push(a//b)
        elif ins == '%':
            a, b = stack.pop(2)
            stack.push(a%b)
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
        elif ins == '|':
            if stack.pop():
                pc.direction = '^'
            else:
                pc.direction = 'v'
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
