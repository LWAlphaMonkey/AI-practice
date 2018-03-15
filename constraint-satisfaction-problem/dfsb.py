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
        if len(argv) != 4:
            print('Invalid input arguments. Usage:')
            print('\tdfsb.py <input_file> <output_file> <mode_flag>')
            sys.exit(-1)

        self.csp = self.parse_input(argv[1])
        self.output = argv[2]
        self.mode = int(argv[3])
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

    def assign_value(self, variable, value, assignment):
        '''
        assign variable and value to assignment
        '''
        self.counter += 1
        assignment[variable] = value

        if self.mode == 1:
            if DEBUG_WITH_BREAK:
                print("variable: ", variable, "value: ", value)
                print(self.csp)
                print("constrants: ", self.csp['C'][variable])
                print([(Xj, variable) for Xj in self.csp['C'][variable]])

            return HEURISTICS().AC3(
                self, [(Xj, variable) for Xj in self.csp['C'][variable]])

        return True

    def unassign_value(self, variable, assignment):
        '''
        unassign variable and value to assignment
        '''
        if variable in assignment:
            assignment.pop(variable)

        if self.mode == 1:
            self.m1_domain[variable] = [
                value for value in range(self.csp['D'])
            ]

    def constraints(self, variable_1, value_1, variable_2, value_2):
        if variable_2 in self.csp['C'][variable_1] and value_1 == value_2:
            return False
        else:
            return True

    def check_conflict(self, variable, value, assignment):
        constraints = self.csp['C'][variable]

        if len(constraints) == 0:
            return True

        for conflict in constraints:
            if conflict in assignment and assignment[conflict] == value:
                return False

        return True

    def count_conflicts(self, variable, value, assignment):
        constraints = self.csp['C'][variable]
        count = 0

        if len(constraints) > 0:
            for conflict in constraints:
                if conflict in assignment and assignment[conflict] == value:
                    count += 1

        if DEBUG_WITH_BREAK:
            print("constraints[%d]: " % variable, constraints)

        return count

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
            if csp.mode == 1:
                m1_domain_backup = copy.deepcopy(csp.m1_domain)

            if csp.check_conflict(variable, value, assignment):

                if csp.mode == 1:
                    csp.m1_domain[variable] = [value]

                inference = csp.assign_value(variable, value, assignment)

                if DEBUG:
                    print('%d. (var: %d, val: %d), assignment: %d\n' %
                          (csp.counter, variable, value, len(assignment)))

                if inference:
                    result = self.recursive_search(assignment, csp)
                    if result is not None:
                        return result

            if csp.mode == 1:
                csp.m1_domain = m1_domain_backup
            csp.unassign_value(variable, assignment)

        return None


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
                1. minimum-remaining-values
                2. degree

        references: AIMA chapter 6.3.1

        '''
        if csp.mode == 0:
            for variable in range(csp.csp['X']):
                if variable not in assignment:
                    return variable
        else:
            # filtered_by_degree = self.degree(assignment, csp)
            modified_variable_list = csp.variable_list[:]
            for variable in assignment:
                modified_variable_list.remove(variable)

            variables = self.minimum_remaining_values(modified_variable_list,
                                                      csp)
            variable = self.degree(variables, csp)

            return variable

    def degree(self, variables, csp):
        '''
        returns one of the most constrained unsigned variables randomly
        '''
        modified_constraint = []

        for variable in variables:
            modified_constraint.append((variable, len(csp.csp['C'][variable])))

        if DEBUG_WITH_BREAK:
            print("iteration: ", csp.counter, "\nassignment: ", assignment,
                  "constraint: ", modified_constraint)

        # max_len = len(modified_constraint[
        max_len = max(modified_constraint, key=lambda x: x[1])

        variables = [
            idx[0] for idx in modified_constraint if idx[1] == max_len[1]
        ]

        if DEBUG_WITH_BREAK:
            print("modified-constraint: ", modified_constraint)
            print("selected variables: ", variables)
            input("")

        return random.choice(variables)

    def minimum_remaining_values(self, variables, csp):
        '''
        returns those unsigned variables which have minimum remaining values
        '''
        if len(variables) == 1:
            return variables
        else:
            ret_value = len(csp.m1_domain[variables[0]])
            ret_variable = []
            for variable in variables:
                curr_value = len(csp.m1_domain[variable])
                if curr_value < ret_value:
                    ret_value = curr_value
                    ret_variable = [variable]

                elif curr_value == ret_value:
                    ret_variable.append(variable)

            return ret_variable

    def order_domain_values(self, variable, assignment, csp):
        '''
        csp.mode = 0 => fixed order
                 = 1 => using least-constraining-value heuristic
        '''
        if csp.mode == 0:
            values = csp.m0_domain[variable][:]
        else:
            value_list = csp.m1_domain[variable]
            conflict_list = [[
                csp.count_conflicts(variable, value, assignment), value
            ] for value in value_list]

            values = [value[1] for value in sorted(conflict_list)]
            csp.m1_domain[variable] = values
            if DEBUG_WITH_BREAK:
                print("values: ", values)
                input("")

        return values

    def AC3(self, csp, queue=None):
        '''
        reference:
            AIMA chapter 6.2.2 
        '''
        if queue == None:
            queue = [(Xi, Xj) for Xi in range(csp.csp['X'])
                     for Xj in csp.csp['C'][Xi]]

        while queue:
            (Xi, Xj) = queue.pop()
            if self.revise(csp, Xi, Xj):
                if len(csp.m1_domain[Xi]) == 0:
                    return False

                for Xk in csp.csp['C'][Xi]:
                    queue.append((Xk, Xi))

        return True

    def revise(self, csp, Xi, Xj):
        '''
        returns true iff we revise the domain of Xi
        reference:
            AIMA chapter 6.2.2 
        '''
        revised = False

        # print('iter: ', csp.counter, '\nXi: ', Xi, 'domain: ',
        #       csp.m1_domain[Xi])
        for value_Xi in csp.m1_domain[Xi]:
            should_remove = True

            # print('Xj: ', Xj, 'domain: ', csp.m1_domain[Xj])
            # input("")
            for value_Xj in csp.m1_domain[Xj]:
                if value_Xi != value_Xj:
                    should_remove = False
                    break

            if should_remove:
                csp.m1_domain[Xi].remove(value_Xi)
                revised = True

        return revised


class TIMER:
    '''
    reference: https://docs.python.org/3/library/signal.html#example
    '''

    def __init__(self, time=60):
        self.time = time
        signal.signal(signal.SIGALRM, self.timeout)
        signal.alarm(self.time)

    def timeout(self, signum, frame):
        raise TimeoutError


def main():
    try:
        TIMER(60)
        start = time.time()

        csp = CSP(sys.argv)

        ret = DFSB().search(csp)
        csp.create_output(ret)
        end = time.time()

        if DEBUG:
            print("iterations: ", csp.counter)
            print('result: ', ret)
            print("%2.2fms" % ((end - start) * 1000))

    except TimeoutError:
        csp.create_output(None)


if __name__ == '__main__':
    main()
