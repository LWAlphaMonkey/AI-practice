import sys
import os
import time
import signal
import copy
import random
"""Map coloring problem"""

DEBUG = True
DEBUG_WITH_BREAK = False


# 1 Input file
# 2 Output file
# 3 mode 0: plain DFS-B,
#        1: DFS-B with variable, value ordering + AC3 for constraint propagation
class CSP:
    '''
    pseudo code references:
        for structure enhancement purpose: http://aima.cs.berkeley.edu/python/csp.html
    '''

    def __init__(self, argv):
        '''
        '''
        if len(argv) != 3:
            print('Invalid input arguments. Usage:')
            print('\tdouble_check.py <input_file> <output_file>')
            sys.exit(-1)

        self.csp = self.parse_input(argv[1])
        self.answer = argv[2]
        self.parse_answer()

    def print_csp(self):
        attrs = vars(self)
        print('\n'.join("%s: %s" % item for item in attrs.items()))

    def parse_answer(self):
        ret = []
        fp = open(self.answer, 'r')
        assignment = fp.readlines()

        self.assign = {}
        variables = [int(val.rstrip('\n')) for val in assignment]

        for idx in range(self.csp['X']):
            self.assign[idx] = variables[idx]

    def parse_input(self, file_name):
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
            ret['X'], constraint_num, ret['D'] = map(
                int,
                fp.readline().rstrip('\n').split('\t'))
            constraints = fp.readlines()

            if len(constraints) != constraint_num:
                raise

            ret['C'] = {val: [] for val in range(ret['X'])}

            for cons in constraints:
                x, y = map(int, cons.rstrip('\n').split('\t'))
                if y not in ret['C'][x]:
                    ret['C'][x].append(y)
                if x not in ret['C'][y]:
                    ret['C'][y].append(x)

            self.variable_list = list(range(ret['X']))

            fp.close()
        except:
            print('Invalid input file')
            fp.close()
            sys.exit(-1)

        return ret

    def create_output(self, assignment):
        fp = open(self.output, 'w')

        if self.goal_test(assignment):
            [
                fp.write(str(assignment[result]) + '\n')
                for result in range(self.csp['X'])
            ]
        else:
            fp.write("No answer")

        fp.close()

        if DEBUG:
            print("\n\n=========================")
            try:
                [
                    print(str(assignment[result]))
                    for result in range(self.csp['X'])
                ]
            except:
                print("No answer")
            print("=========================\n\n")

    def goal_test(self, assignment):
        '''
        check the assignment is correct or not
        '''
        if assignment is None:
            return False

        for variable in assignment:
            constraints = self.csp['C'][variable]
            if len(constraints) == 0:
                continue
            for conflict in constraints:
                if conflict in assignment and assignment[conflict] == assignment[variable]:
                    return False

        return True


def main():
    csp = CSP(sys.argv)
    if csp.goal_test(csp.assign):
        print("The assignment is correct")


if __name__ == '__main__':
    main()
