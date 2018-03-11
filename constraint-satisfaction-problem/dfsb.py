import sys
import os
import time
import copy
import heapq
import queue
"""Map coloring problem"""

DEBUG = True


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
        assign
        current_domain
        '''
        if len(argv) != 4:
            print('Invalid input arguments. Usage:')
            print('\tdfsb.py <input_file> <output_file> <mode_flag>')
            sys.exit(-1)

        self.csp = self.parse_input(argv[1])
        self.output = argv[2]
        self.mode = int(argv[3])

        self.input_checking()

        self.assign = {}
        # self.m0_domain = {}
        self.m1_domain = {}
        self.counter = 0

    def input_checking(self):
        '''
        input argument checking, if mode is not 0 or 1, exit
        '''
        if self.mode != 0 and self.mode != 1:
            print('Invalid input file')
            sys.exit(-1)

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
            ret['X'], ret['C']['counts'], ret['D'] = map(
                int,
                fp.readline().rstrip('\n').split('\t'))
            constraints = fp.readlines()

            if len(constraints) != ret['C']['counts']:
                raise

            ret['C']['constraint'] = {val: [] for val in range(ret['X'])}

            for cons in constraints:
                x, y = map(int, cons.rstrip('\n').split('\t'))
                if y not in ret['C']['constraint'][x]:
                    ret['C']['constraint'][x].append(y)
                if x not in ret['C']['constraint'][y]:
                    ret['C']['constraint'][y].append(x)

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

    def assign_value(self, variable, value, assignment):
        '''
        assign variable and value to assignment
        '''
        self.counter += 1
        self.assign[variable] = value
        assignment[variable] = value

    def unassign_value(self, variable, assignment):
        '''
        unassign variable and value to assignment
        '''
        assignment.pop(variable)

    def check_conflict(self, variable, value, assignment):
        constraints = self.csp['C']['constraint'][variable]

        if len(constraints) == 0:
            return True

        for conflict in constraints:
            if conflict in assignment and assignment[conflict] == value:
                return False

        return True

    def goal_test(self, assignment):
        '''
        check the assignment is correct or not
        '''
        if assignment is None:
            return False

        for variable in assignment:
            constraints = self.csp['C']['constraint'][variable]
            if len(constraints) == 0:
                continue
            for conflict in constraints:
                if conflict in assignment and assignment[conflict] == assignment[variable]:
                    return False

        return True


class DFSB:
    '''
    pseudo code references:
        DFSB: AIMA [Fig 6.5]
    '''

    def search(self, csp):
        '''
        returns a solution, or failure
        '''
        return self.recursive_search({}, csp)

    def recursive_search(self, assignment, csp):
        '''
        returns a solution, or failure
        '''
        if len(assignment) == csp.csp['X']:
            return assignment

        variable = HEURISTICS().select_unsigned_variable(assignment, csp)

        for value in HEURISTICS().order_domain_values(variable, assignment,
                                                      csp):
            csp.assign_value(variable, value, assignment)
            if DEBUG:
                print('%d. (var: %d, val: %d), assignment: %d\n' %
                      (csp.counter, variable, value, len(assignment)))

            if csp.check_conflict(variable, value, assignment):

                result = self.recursive_search(assignment, csp)

                if result is not None:
                    return result

            csp.unassign_value(variable, assignment)


class HEURISTICS:
    '''
    variable ordering purpose: select_unsigned_variable
    value ordering purpose: order_domain_values
    inference purpose: AC_3
    '''

    def select_unsigned_variable(self, assignment, csp):
        '''

        '''
        if csp.mode == 0:
            for var in range(csp.csp['X']):
                if var not in assignment:
                    return var
        else:
            modified_constraint = copy.deepcopy(csp.csp['C']['constraint'])
            if DEBUG:
                print("iteration: ", csp.counter, "\nassignment: ", assignment,
                      "constraint: ", modified_constraint)

            for variable in assignment:
                modified_constraint.pop(variable)

            var = max(
                modified_constraint,
                key=lambda idx: len(modified_constraint[idx]))

            if DEBUG:
                print("modified-constraint: ", modified_constraint)
                print("selected variable: ", var)
                input("")

            return var

    def order_domain_values(self, variable, assignment, csp):
        '''
        csp.mode = 0 => fixed order
                 = 1 => using least-constraining-value heuristic
        '''
        if csp.mode == 0:
            values = [val for val in range(csp.csp['D'])]
        else:
            values = [val for val in range(csp.csp['D'])]

        return values

    def AC_3(self, csp):
        '''
        '''
        pass

    def revise(self, Xi, Xj):
        '''
        '''
        pass


def main():
    start = time.time()

    csp = CSP(sys.argv)

    ret = DFSB().search(csp)
    csp.create_output(ret)
    end = time.time()

    if DEBUG:
        print('csp: ', csp.csp)
        print('output: ', csp.output)
        print('mode: ', csp.mode)
        print("%2.2fms" % ((end - start) * 1000))


if __name__ == '__main__':
    main()
