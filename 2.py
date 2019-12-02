import sys
from tqdm import tqdm
def calc(ns, a, b):
    ns = ns[:]
    ns[1] = a
    ns[2] = b
    pc = 0
    try:
        while True:
            if ns[pc] == 1:
                ns[ns[pc+3]] = ns[ns[pc+1]] + ns[ns[pc+2]]
            elif ns[pc] == 2:
                ns[ns[pc+3]] = ns[ns[pc+1]] * ns[ns[pc+2]]
            elif ns[pc] == 99:
                return ns[0]
            else:
                assert False
            pc += 4
    except IndexError:
        return False
if __name__ == '__main__':
    ns = [int(n) for n in sys.stdin.read().rstrip('\n').split(',')]
    print('part 1:', calc(ns, 12, 2))
    print('part 1:', calc(ns, 12, 2))
    for a in tqdm(range(1000)):
        for b in range(1000):
            if calc(ns, a, b) == 19690720:
                print(a, b, 100*a+b)
