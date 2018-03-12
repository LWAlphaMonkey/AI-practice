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
        self.assign = {}
        self.m0_domain = {}
        self.m1_domain = {}
        self.counter = 0

        self.input_checking()

        if self.mode == 0:
            self.init_m0_domain()
        else:
            self.init_m1_domain()

    def print_csp(self):
        attrs = vars(self)
        print('\n'.join("%s: %s" % item for item in attrs.items()))

    def input_checking(self):
        '''
        input argument checking, if mode is not 0 or 1, exit
        '''
        if self.mode != 0 and self.mode != 1:
            print('Invalid input file')
            sys.exit(-1)

    def init_m0_domain(self):
        for variable in range(self.csp['X']):
            self.m0_domain[variable] = [
                value for value in range(self.csp['D'])
            ]

    def init_m1_domain(self):
        for variable in range(self.csp['X']):
            self.m1_domain[variable] = [
                value for value in range(self.csp['D'])
            ]

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
        if self.mode == 1:
            HEURISTICS().AC3(self, [(Xk, var) for Xk in self.neighbors[var]])

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

    def count_conflicts(self, variable, value, assignment):
        constraints = self.csp['C']['constraint'][variable]
        count = 0

        if len(constraints) > 0:
            for conflict in constraints:
                if conflict in assignment and assignment[conflict] == value:
                    count += 1

        if DEBUG:
            print("constraints[%d]: " % variable, constraints)

        return count

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
    references:
        AIMA chapter 6.3.1
    '''

    def select_unsigned_variable(self, assignment, csp):
        '''
        case DFSB plain:
            select unsigned variable in a fixed order
        case DFSB++:
            select unsigned variable based on the following heuristics:
                1. degree
                2. minimum-remaining-values

        references: AIMA chapter 6.3.1

        '''
        if csp.mode == 0:
            for var in range(csp.csp['X']):
                if var not in assignment:
                    return var
        else:
            filtered_by_degree = self.degree(assignment, csp)
            var = self.minimum_remaining_values(filtered_by_degree, csp)
            print("select unsigned variable:", var)

            return var

    def degree(self, assignment, csp):
        '''
        returns those most constrained unsigned variables
        '''
        modified_constraint = copy.deepcopy(csp.csp['C']['constraint'])
        variables = []

        if DEBUG:
            print("iteration: ", csp.counter, "\nassignment: ", assignment,
                  "constraint: ", modified_constraint)

        for variable in assignment:
            modified_constraint.pop(variable)

        max_len = len(modified_constraint[max(
            modified_constraint,
            key=lambda idx: len(modified_constraint[idx]))])

        variables = [
            idx for idx in modified_constraint
            if len(modified_constraint[idx]) == max_len
        ]

        if DEBUG:
            print("modified-constraint: ", modified_constraint)
            print("selected variables: ", variables)
            input("")

        return variables

    def minimum_remaining_values(self, variables, csp):
        '''
        returns one unsigned variable which has minimum remaining values
        '''
        if len(variables) == 1:
            return variables
        else:
            ret_value = len(csp.m1_domain[variables[0]])
            ret_variable = variables[0]
            for variable in variables:
                curr_value = len(csp.m1_domain[variable])
                if curr_value < ret_value:
                    ret_value = curr_value
                    ret_variable = variable

            return ret_variable

    def order_domain_values(self, variable, assignment, csp):
        '''
        csp.mode = 0 => fixed order
                 = 1 => using least-constraining-value heuristic
        '''
        if csp.mode == 0:
            values = csp.m0_domain[variable]
        else:
            values = csp.m1_domain[variable]
            conflict_list = [[
                csp.count_conflicts(variable, value, assignment), value
            ] for value in values]
            values = [value[1] for value in sorted(conflict_list)]

            if DEBUG:
                print("values: ", values)
                input("")

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
        # print('csp.csp: ', csp.csp)
        # print('csp.mode:', csp.mode)
        # print('csp.')
        csp.print_csp()
        print('output: ', csp.output)
        print('mode: ', csp.mode)
        print("%2.2fms" % ((end - start) * 1000))


if __name__ == '__main__':
    main()
