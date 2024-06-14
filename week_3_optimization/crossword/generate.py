import sys

from crossword import *

import copy


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
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
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
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

        domain_copy = copy.deepcopy(self.domains)

        for var in domain_copy:
            var_len = var.length
            possible_words = domain_copy[var]

            for word in possible_words:
                if len(word) != var_len:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        # cuz this returns tuple of **where** word 1 needs to be equal to word 2
        x_overlap, y_overlap = self.crossword.overlaps[x, y]

        revision = False

        domain_copy = copy.deepcopy(self.domains)

        if x_overlap:
            for word_x in domain_copy[x]:
                matched = False

                for word_y in self.domains[y]:

                    if word_x[x_overlap] == word_y[y_overlap]:
                        matched = True
                        break
                        # don't need to check all the other words with this one
                if matched:
                    continue
                else:
                    self.domains[x].remove(word_x)
                    revision = True

        return revision

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        if not arcs:
            # If `arcs` is None, begin with initial list of all arcs in the problem.
            queue = []

            for var_1 in self.domains:
                for var_2 in self.crossword.neighbors(var_1):
                    if self.crossword.overlaps[var_1, var_2] != None:
                        queue.append((var_1, var_2))

            while len(queue) > 0:
                var_x, var_y = queue.pop(0)

                if self.revise(var_x, var_y):
                    if len(self.domains[var_x]) == 0:
                        return False

                    for neighbor in self.crossword.neighbors(var_x):
                        if neighbor != var_y:
                            queue.append((neighbor, var_x))

                return True

            return False

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.domains:
            if var not in assignment:
                return False

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        words = [*assignment.values()]
        if len(words) != len(set(words)):
            return False

        for var in assignment:
            if var.length != len(assignment[var]):
                return False

        for var in assignment:
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    x_overlap, y_overlap = self.crossword.overlaps[var, neighbor]
                    if assignment[var][x_overlap] != assignment[neighbor][y_overlap]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        words_elim = {}

        neighbors = self.crossword.neighbors(var)

        for word in self.domains[var]:
            num_eliminated = 0

            for neighbor in neighbors:

                if neighbor in assignment:
                    continue

                else:

                    x_overlap, y_overlap = self.crossword.overlaps[var, neighbor]
                    for word_neighbor in self.domains[neighbor]:
                        # iterate through neighbour's words, check for eliminate ones
                        if word[x_overlap] != word_neighbor[y_overlap]:
                            num_eliminated += 1

            words_elim[word] = num_eliminated

        sorted_items = sorted(words_elim.items(), key=lambda item: item[1])

        sorted_words = dict(sorted_items)

        return list(sorted_words.keys())

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        min_choices = {}

        for var in self.domains:

            if var not in assignment:
                min_choices[var] = self.domains[var]

        sorted_items = dict(sorted(min_choices.items(), key=lambda item: len(item[1])))

        return list(sorted_items.keys())[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        if len(assignment) == len(self.domains):
            return assignment

        var = self.select_unassigned_variable(assignment)

        for val in self.domains[var]:

            copy_assignment = assignment.copy()
            copy_assignment[var] = val

            if self.consistent(copy_assignment):
                result = self.backtrack(copy_assignment)
                if result is not None:
                    return result
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
