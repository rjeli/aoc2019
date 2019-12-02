#!/usr/bin/env python3

import sys

if __name__ == '__main__':
    masses = [int(l.strip()) for l in sys.stdin.readlines()]
    print('part 1:', sum(m//3-2 for m in masses))
    total_fuel = 0
    for m in masses:
        while True:
            m = m//3-2
            if m <= 0:
                break
            total_fuel += m
    print('part 2:', total_fuel)

