import sys
import os
import time
import heapq
"""Map coloring problem"""

DEBUG = False


# 1 Input file
# 2 Output file
# 3 mode 0: plain DFS-B,
#        1: DFS-B with variable, value ordering + AC3 for constraint propagation
class CSP:
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
        self.domains = {}
        self.current_domain = {}

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

            if DEBUG:
                print('variables:', ret['X'], ' constraints:', constraint,
                      ' doma/ins:', ret['D'])
                print(ret)

        return ret

    def input_checking(self):
        '''
        input argument checking, if mode is not 0 or 1, exit
        '''
        if self.mode != 0 and self.mode != 1:
            print('Invalid input file')
            sys.exit(-1)

    def create_output(self, assignment):
        fp = open(self.output, 'w')

        if self.goal_test(assignment):
            [fp.write(str(assignment[result]) + '\n') for result in assignment]

            if DEBUG:
                print("The assignment is correct")
                print(ret)
        else:
            fp.write("No answer")

        fp.close()

    def assign_value(self, variable, value, assignment):
        '''
        assign variable and value to assignment
        '''
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
        for variable in assignment:
            constraints = self.csp['C']['constraint'][variable]
            if len(constraints) == 0:
                continue
            for conflict in constraints:
                if conflict in assignment and assignment[conflict] == assignment[variable]:
                    return False
        return True


class DFSB:
    def search(self, csp):
        '''
        returns a solution, or failure
        '''
        return self.recursive_search({}, csp)

    def recursive_search(self, assignment, csp):
        '''
        returns a solution, or failure
        csp.mode = 0 => return DFSB result
                 = 1 => return DFSB++ result
        '''
        if len(assignment) == csp.csp['X']:
            return assignment

        variable = self.select_unsigned_variable(assignment, csp)

        for value in self.order_domain_values(variable, assignment, csp):
            csp.assign_value(variable, value, assignment)

            if csp.check_conflict(variable, value, assignment):
                result = self.recursive_search(assignment, csp)

                if result is not None:
                    return result

            csp.unassign_value(variable, assignment)

        # if csp.mode == 0:
        #     if DEBUG:
        #         print("Plain DFS")
        # else:
        #     if DEBUG:
        #         print("DFSB++")
        #     var = select_unsigned_variable(csp)

        # for value in order_domain_values(var, assignment, csp):

    def recursive_plus_plus(self, assignment, csp):
        if DEBUG:
            print("DFSB++")

    def select_unsigned_variable(self, assignment, csp):
        '''
        csp.mode = 0 => fixed order
                 = 1 => using minimum-remaining-value heuristic 
                        and degree heuristic
        '''
        if csp.mode == 0:
            if DEBUG:
                print("Plain DFS: select unsigned variable")

            for var in range(csp.csp['X']):
                if var not in assignment:
                    return var
        else:
            if DEBUG:
                print("DFSB++: select unsigned variable")
        return csp

    def order_domain_values(self, variable, assignment, csp):
        '''
        csp.mode = 0 => fixed order
                 = 1 => using least-constraining-value heuristic
        '''
        if csp.mode == 0:
            if DEBUG:
                print("Plain DFS: order domain values")

            values = [val for val in range(csp.csp['D'])]
        else:
            if DEBUG:
                print("DFSB++: order domain values")
            values = []

        return values


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
