import itertools
import random

debugmode = False

class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count==len(self.cells):
            return self.cells
        else:
            return set()
        
    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count==0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1
            if self.count < 0:
                exit(f"incorrect count={self.count}, after mark {cell} as mine")
        return

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)
        return

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """            
        if debugmode:
            print(f'Mark cell {cell} as safe, and it has {count} mines nearby\n')
            print('Current mines are:\n')
            print(','.join(['('+str(x[0])+','+str(x[1])+')' for x in self.mines]))
            print('\n')
            print('Current safes are\n')
            print(','.join(['('+str(x[0])+','+str(x[1])+')' for x in self.safes]))
            print('\n')
            print('Current knowledge are\n')
            for x in self.knowledge:
                print(f'{x}\n')
        self.moves_made.add(cell)
        self.mark_safe(cell)
        nearby_potential_mines = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Ignore the cell itself
                if (i, j) == cell:
                    continue
                if 0 <= i < self.height and 0 <= j < self.width:
                    # only include the cells that are not known
                    if (i,j) in self.safes:
                        continue
                    if (i,j) in self.mines:
                        count -= 1
                    else:
                        nearby_potential_mines.add((i,j))
        #check whether we can end the game earlier
        #if len(self.mines)+len(self.safes) == self.height*self.width:
        #    self.moves_made = self.safes
        # important: for cases when count=0 or count=len(nearby_potential_mines),
        # we must add as a new sentence, instead of directly mark as safe or mark as mines
        # because the new sentence may be combined with other knowledge to infer more new sentences 
        self.knowledge.append(Sentence(nearby_potential_mines, count))
        if debugmode:
            print(f'add knowledge:{self.knowledge[-1]}\n')

        update = True
        while update:
            update = False
            # three types of knowledge will be checked:
            # 1. Whether known_mines can be inferred
            # 2. Whether known_safes can be inferred
            # 3. Whether new knowledge can be inferred using subset method:
            # ie: if set1=count1, set2=count2, where set1 is a subset of set2
            # when set2-set1= count2-count1
            removelist = set()
            for si in range(len(self.knowledge)):
                ms = self.knowledge[si].known_mines()
                if len(ms):
                    update = True
                    if debugmode:
                        print(f'knowledge is:{self.knowledge[si]}, mark new mines:{ms}\n')
                    for m in ms.copy():
                        self.mark_mine(m)
                ss = self.knowledge[si].known_safes()
                if len(ss):
                    update = True
                    if debugmode:
                        print(f'knowledge is {self.knowledge[si]}, mark new safes: {ss}\n')
                    for s in ss.copy():
                        self.mark_safe(s)
                if self.knowledge[si].count==0 and len(self.knowledge[si].cells)==0:
                    removelist.add(si)

            knowlen = len(self.knowledge)
            for si in range(knowlen):
                for sj in range(knowlen):
                    if si!=sj and self.knowledge[si].count>0 and \
                        self.knowledge[si].count<=self.knowledge[sj].count and \
                        self.knowledge[si].cells.issubset(self.knowledge[sj].cells) and \
                        not self.knowledge[sj].cells.issubset(self.knowledge[si].cells):
                        update = True
                        removelist.add(sj)
                        newcells = self.knowledge[sj].cells.difference(self.knowledge[si].cells)
                        self.knowledge.append(Sentence(newcells, self.knowledge[sj].count-self.knowledge[si].count))
                        if debugmode:
                            print(f'Found knowledge {self.knowledge[si]} is subset of {self.knowledge[sj]}.')
                            print(f'Add new knowledge {self.knowledge[-1]}\n')
            # remove empty sentence or redundant sentence due to subset inference method
            for si in reversed(range(len(self.knowledge))):
                if si in removelist:
                    del self.knowledge[si]             
            if debugmode:
                print(f'update is {update}\n')
                print(f'Mark cell {cell} as safe, and it has {count} mines nearby\n')
                print('Current mines are:\n')
                print(','.join(['('+str(x[0])+','+str(x[1])+')' for x in self.mines]))
                print('\n')
                print('Current safes are\n')
                print(','.join(['('+str(x[0])+','+str(x[1])+')' for x in self.safes]))
                print('\n')
                print('Current knowledge are\n')
                for x in self.knowledge:
                    print(f'{x}\n')
                print('\n\n\n\n')


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        candidates = self.safes.difference(self.moves_made)
        if len(candidates):
            return list(candidates)[0]
        else:
            return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        if len(self.mines)+len(self.moves_made) == self.height*self.width:
            return None
        candidates = set()
        for i in range(self.height):
            for j in range(self.width):
                if (i,j) not in self.mines and (i,j) not in self.moves_made:
                    candidates.add((i,j))
        if len(candidates):
            return random.sample(list(candidates), 1)[0]
        else:
            return None

