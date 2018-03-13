import sys
import time
import random
import signal

DEBUG = False


class CSP:
    def __init__(self, argv):
        if len(argv) != 3:
            print('Invalid input arguments. Usage:')
            print('\tminconflicts.py <input_file> <output_file>')
            sys.exit(-1)

        self.csp = self.parse_input(argv[1])
        self.output = argv[2]
        self.counter = 0
        self.domain = self.init_domain()
        self.assign = self.initial_complete_assignment()
        self.last_variable = 0

    def parse_input(self, file_name):
        '''
        parse input file
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

    def init_domain(self):
        ret = {}

        for variable in range(self.csp['X']):
            ret[variable] = [value for value in range(self.csp['D'])]

        return ret

    def create_output(self, assignment):
        '''
        write the searching result
        '''
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

    def initial_complete_assignment(self):
        '''
        randomly assign the value to each variable
        returns a complete assignment
        '''
        assignment = {}

        for variable in range(self.csp['X']):
            assignment[variable] = random.choice(range(self.csp['D']))

        return assignment

    def assign_value(self, variable, value):
        '''
        assign variable and value to assignment
        '''
        self.counter += 1
        self.assign[variable] = value

    def count_conflicts(self, variable, value):
        constraints = self.csp['C']['constraint'][variable]
        count = 0

        if len(constraints) > 0:
            for conflict in constraints:
                if self.assign[conflict] == value:
                    count += 1

        if DEBUG:
            print("constraints[%d]: " % variable, constraints)

        return count

    def get_conflict_list(self):
        '''

        '''
        conflict_list = []

        for idx in self.assign:
            if self.count_conflicts(idx, self.assign[idx]) > 0:
                conflict_list.append(idx)

        if DEBUG:
            print("constraints: ", self.csp['C']['constraint'])
            print("current assignment: ", self.assign)
            print("conflict list: ", conflict_list)

        return conflict_list

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


class MINCONFLICTS:
    '''
    min-conflicts local search heuristic
    '''

    def __init__(self):
        '''
        tabu_list: a list of visited states and forbidding the algorithm to retun to these states 
        last_variable: keeps the last randomly selected variable to avoid picking the same variable continuously
        '''
        self.tabu_list = {}
        self.last_variable = 0

    def main_process(self, csp, max_steps=1000000):
        '''
        returns a solution or failure
        inputs: csp, a constraint satisfaction problem
        max_steps: the number of steps allowed before giving up
        '''
        count = 0
        valid_assign = False

        for iteration in range(max_steps):

            if csp.goal_test(csp.assign):
                csp.counter = iteration
                return csp.assign

            conflict_list = csp.get_conflict_list()

            while True:
                variable = random.choice(conflict_list)
                if variable != self.last_variable:
                    self.last_variable = variable
                    break

            conflict_list = [[csp.count_conflicts(variable, value), value]
                             for value in csp.domain[variable]]
            values = [value[1] for value in sorted(conflict_list)]

            for value in values:
                csp.assign_value(variable, value)
                key = ''.join("%d" % val for (key, val) in csp.assign.items())
                if key not in self.tabu_list:
                    self.tabu_list[key] = 1
                    valid_assign = True
                    break

            if not valid_assign:
                count += 1

            valid_assign = False

            if count == 100:
                count = 0
                csp.initial_complete_assignment()

        return csp.assign


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
        TIMER(30)
        start = time.time()
        csp = CSP(sys.argv)
        ret = MINCONFLICTS().main_process(csp)

        end = time.time()
        csp.create_output(ret)

        if DEBUG:
            if ret:
                print("# of iterations: ", csp.counter)
                print('result: \n', ret)
            else:
                print("fail")
            print("%2.2fms" % ((end - start) * 1000))

    except TimeoutError:
        csp.create_output(None)


if __name__ == '__main__':
    main()
