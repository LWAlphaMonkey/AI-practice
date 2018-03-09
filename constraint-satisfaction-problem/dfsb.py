import sys
import os
import time
"""Map coloring problem"""


# 1 Input file
# 2 Output file
# 3 mode (0: plain DFS-B, 1: DFS-B with variable, value ordering + AC3 for constraint propagation)
class CSP:
    def __init__(self, argv):
        if len(argv) != 4:
            print('Invalid input arguments. Usage:')
            print('\tdfsb.py <input_file> <output_file> <mode_flag>')
            sys.exit(-1)

        self.csp = self.parseInput(argv[1])
        self.output = argv[2]
        self.mode = int(argv[3])
        self.inputChecking()

    def parseInput(self, file_name):
        '''
        inputs: input file
        returns: csp {
                      'X': variables
                      'D': domains
                      'C':{'counts': number of counstraints
                           'counstraint': each constraint}
                      }
        '''

        ret = {}
        fp = open(file_name, 'r')

        try:
            ret['C'] = {}
            ret['C']['constraint'] = []
            ret['X'], ret['C']['counts'], ret['D'] = map(
                int,
                fp.readline().rstrip('\n').split('\t'))
            constraints = fp.readlines()

            if len(constraints) != ret['C']['counts']:
                raise

            for cons in constraints:
                (x, y) = map(int, cons.rstrip('\n').split('\t'))
                ret['C']['constraint'].append((x, y))

            fp.close()
        except:
            print('Invalid input file')
            fp.close()
            sys.exit(-1)

            print('variables:', ret['X'], ' constraints:', constraint,
                  ' doma/ins:', ret['D'])
            print(ret)

        return ret

    def inputChecking(self):
        '''
        input argument checking, if mode is not 0 or 1, exit
        '''
        if self.mode != 0 and self.mode != 1:
            print('Invalid input file')
            sys.exit(-1)


def main():
    csp = CSP(sys.argv)
    print('csp: ', csp.csp)
    print('output: ', csp.output)
    print('mode: ', csp.mode)


if __name__ == '__main__':
    main()
