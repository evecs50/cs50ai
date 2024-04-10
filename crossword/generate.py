import sys
import copy
from crossword import *


class CrosswordCreator():

    def __init__(self, crossword, debugmode=False):
        """
        Create new CSP crossword generate.
        """
        self.debugmode = debugmode
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox(
                            (0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for x in self.domains.keys():
            for val in self.domains[x].copy():
                if len(val) != x.length:
                    self.domains[x].remove(val)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.
        consistent pair of domain values have to satisfy:
        1. distinct
        2. if x and y overlaps, they have to be identical on the overlapped index
        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        debug_prefix = "---revise---:"
        revised = False

        for val1 in self.domains[x].copy():
            need_remove = False
            if self.crossword.overlaps.get((x, y)):
                id1, id2 = self.crossword.overlaps.get((x, y))
                if self.debugmode:
                    print(f'''{debug_prefix} Variable {x} with domain {self.domains[x]} and variable {y} with 
                          domain {self.domains[y]}, require consistency {(id1,id2)}''')
                if not any(val1[id1] == val2[id2] and val1 != val2 for val2 in self.domains[y]):
                    need_remove = True
            else:
                if not any(val1 != val2 for val2 in self.domains[y]):
                    need_remove = True
            if need_remove:
                self.domains[x].remove(val1)
                revised = True
                if self.debugmode:
                    print(
                        f'{debug_prefix} Remove {val1} from x\'s domain, domain changes to {self.domains[x]}')

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        debug_prefix = '---ar3---:'
        if arcs is None:  # do not use "if not arcs"
            arcs = [(x, y) for x in self.domains.keys()
                    for y in self.domains.keys() if x != y]
        if self.debugmode:
            print(f'{debug_prefix} Initial queue is {arcs}')

        while arcs:
            (x, y) = arcs.pop()
            if self.revise(x, y):
                if self.debugmode:
                    print(f'{debug_prefix} Revise on variable {x} is made')
                if len(self.domains[x]) == 0:  # Inconsistent
                    if self.debugmode:
                        print(f'{debug_prefix} Arc {x} and {y} are inconsistent')
                    return False
                # Add all arcs of [z, x] to the queue where z is in x.neighbour - y
                addqueue = [(z, x) for z in self.crossword.neighbors(
                    x) if z != y and (z, x) not in arcs]
                arcs.extend(addqueue)
                if self.debugmode:
                    print(
                        f'{debug_prefix} Add additional arcs to the queue: {addqueue}')

        return True  # Consistent

    def dequeue(self, queue):
        for x, y in queue:
            queue.remove((x, y))
            return (x, y)

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return len(assignment) == len(self.domains)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # distinct values
        value_set = set(assignment.values())
        if len(value_set) != len(assignment.values()):
            return False

        # correct length
        for var in assignment.keys():
            if len(assignment[var]) != var.length:
                return False

        # neighbor consistent
        for x in assignment.keys():
            for y in self.crossword.neighbors(x):
                if y not in assignment:
                    continue
                if self.crossword.overlaps[x, y]:
                    id1, id2 = self.crossword.overlaps[x, y]
                    if assignment[x][id1] != assignment[y][id2]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        debug_prefix = '---order_domain_values---:'
        domain_ruleout = {val: 0 for val in self.domains[var]}
        neighbors = self.crossword.neighbors(var)
        for val in self.domains[var]:
            for y in neighbors:
                if self.crossword.overlaps.get((var, y)):
                    id1, id2 = self.crossword.overlaps.get((var, y))
                    # domain_ruleout[val] += sum([val[id1]!=val2[id2] or val==val2 for val2 in self.domains[y]])
                    domain_ruleout[val] += sum([val[id1] != val2[id2]
                                               for val2 in self.domains[y]])
                # else:
                #    domain_ruleout[val] += sum([val==val2 for val2 in self.domains[y]])

        if self.debugmode:
            print(f'{debug_prefix} domain_ruleout for {var} is\n{domain_ruleout}')
        return sorted(domain_ruleout, key=domain_ruleout.get)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        debug_prefix = '---select_unassigned_vairable---:'
        min_val = float('Inf')
        min_var = []
        for variable in self.domains.keys():
            if variable not in assignment:
                if len(self.domains[variable]) <= min_val:
                    min_val = len(self.domains[variable])
                    min_var.append(variable)
        if len(min_var) > 1:  # 'degree':
            max_degree = float('-Inf')
            max_var = None
            for variable in min_var:
                if len(self.crossword.neighbors(variable)) >= max_degree:
                    max_degree = len(self
                                     .crossword.neighbors(variable))
                    max_var = variable
            return max_var
        else:
            return min_var[0]
        """
        unassigned = set(self.domains.keys()) - set(assignment.keys())

        # Create list of variables, sorted by MRV and highest degree
        result = [var for var in unassigned]
        result.sort(key = lambda x: (len(self.domains[x]), -len(self.crossword.neighbors(x))))
        """

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        debug_prefix = '---backtrack---:'

        # Check if assignment is complete
        if self.assignment_complete(assignment):
            return assignment

        orig_domains = copy.deepcopy(self.domains)
        if self.debugmode:
            print(f'{debug_prefix} Current assignment is\n{assignment}')
            print(f'{debug_prefix} Current domain is\n{self.domains}')

        # Try a new variable
        new_var = self.select_unassigned_variable(assignment)
        if self.debugmode:
            print(f'{debug_prefix} Select unassigned variable {new_var}')
        sorted_domain = self.order_domain_values(new_var, assignment)
        if self.debugmode:
            print(f'{debug_prefix} Sorted_domain is {sorted_domain}')

        for value in sorted_domain:
            new_assignment = assignment.copy()
            new_assignment[new_var] = value
            if self.consistent(new_assignment):
                if self.debugmode:
                    print(f'{debug_prefix} Try new assignment: {new_var}={value}')
                    print(f'{debug_prefix} New assignment is\n{new_assignment}')
                    print(f'{debug_prefix} Current domain is\n{self.domains}')
                # Run arc-consistency check
                init_arcs = [(y, new_var)
                             for y in self.crossword.neighbors(new_var)]
                self.domains[new_var] = {value}
                if init_arcs is None or self.ac3(init_arcs):
                    if self.debugmode:
                        print(f'{debug_prefix} ac3 is successful')
                    result = self.backtrack(new_assignment)
                    if result is not None:
                        return result
                else:
                    if self.debugmode:
                        print(
                            f'{debug_prefix} New assignment {new_var}={value} failed.')

                self.domains = copy.deepcopy(orig_domains)
                if self.debugmode:
                    print(f'{debug_prefix} Restore domain')

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
