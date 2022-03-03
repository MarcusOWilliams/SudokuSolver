
import numpy as np
import math

#This sudoku solver is an implementation of algorithm X by Donald Knuth to solve a sudoku as an exact cover problem
#It implements the Dancing Links technique (DLX) which involves adding and deleting data to a doubly linked circular list

#This node class is used for the circular doubly linked list to make up the rows
class Node:
    def __init__(self) -> None:
        self.row = None
        self.up = None
        self.down = None
        self.left = None
        self.right = None
        self.head = None


            

#This is a sepcial version of the node class which is used as the header of each column in our constraint matrix       
class Header(Node):
    def __init__(self) -> None:
        self.count = None
        self.left = None
        self.right = None
        self.index = None



#this is the main class which takes a sudoku as a numpy array
class Sudoku():
    #the init function takes the sudoku as a np array
    def __init__(self, grid):

        self.grid = grid

        #to start the solved sudoku is just the original and the solution is empty
        self.solvedSudoku = np.copy(grid)
        self.solution = []
        
        #the sudoku can have a varying size, as long as it is square, normal sodokus are 9x9, so gridSize would be 9
        self.gridSize = len(grid)

        #the number of columns and rows required for our constraint matrix are based on the size of the grid

        self.numCols = (self.gridSize * self.gridSize * 4) + 1 # add one for the root node
        self.numRows = (self.gridSize ** 3)

        #create lists of Nodes() to make up the rows, each row is a possible number in a cell in the sudoku and each of these has 4 constraints/nodes
        #The cols list is made up of Headers, these are the top of each column
        self.rows = [[Node() for i in range(4)] for n in range(self.numRows)]
        self.cols = [Header() for i in range(self.numCols)]

        #the root node is a special node which acts as an access point to all other column headers
        self.rootNode = self.cols[-1]

        self.isSolved = False

    #This function generates the constraint matrix, I found a great visulisation of what this function is trying to create here: https://www.stolaf.edu//people/hansonr/sudoku/exactcovermatrix.htm
    def generateConstraintMatrix(self):

        numCols = self.numCols
        numRows = self.numRows
        cols = self.cols
        rows =self.rows
        grid = self.grid
        gridSize = self.gridSize

        #create headers
        for i in range(numCols):
            
            #the count is orignally 0, this is the number of Nodes in a given column
            cols[i].count = 0
            #the index just acts as an easy way to identify the columns if needed
            cols[i].index = i

            #the columns up pointer is intially pointing to itself and so is the down pointer
            cols[i].up = cols[i]
            cols[i].down = cols[i]

            #the left and right pointers point the the previous and next columns in the list respectivley
            cols[i].left = cols[(i + numCols -1) % numCols]
            cols[i].right = cols[(i+1)%numCols]

        #these variables are used to make it easier to calculate values in upcoming steps
        sqGridSize = gridSize * gridSize
        boxSize = int(math.sqrt(gridSize))

        #This generates the nodes present in the constraint matrix rows
        for i in range(numRows):
            
            #the values for the respective rows and columns in the orignal grid are calculated
            currentRow = i//sqGridSize
            currentCol = (i// gridSize) % gridSize

            offset = (i % gridSize) #the value constrinat

            currentCell = grid[currentRow][currentCol]

             
            #each filled in cell from the origninal sudoku will get one constraint, when the offset+1 (e.g. 1-9, is the same as the value in the cell)
            #otherwise it will be caught by this if statement and skipped
            #This is necessary because you must only have one of each constraint for the givens, rather than the 9 you have for the unknowns due to the different possabilities
            #This will fill out the exact cover matrix for given the sudoku
            #If the cell is known then there is one Node for each constraint
            #if the cell is not known then there is 9 Nodes added for each constraint because of the 9 possibilities
            

            if currentCell != 0 and currentCell != offset+1:
                continue
                
            #each row has 4 constraints, explained by the exact cover version of a sudoku
            #for each constraint the column in the constraint matrix needs to be calculated
            for j in range(4):

                columnStart = j * sqGridSize
                columnIndex = 0
                if j == 0: #cell contraints
                    columnIndex = i//gridSize
                elif j == 1: #row constraint
                    columnIndex = columnStart + (currentRow * gridSize) + offset
                elif j == 2: #column constrint
                    columnIndex = columnStart + currentCol * gridSize + offset
                elif j == 3: #box constraint
                    columnIndex = columnStart + (boxSize * (currentRow // boxSize) + (currentCol//boxSize)) * gridSize +offset

                columnIndex = int(columnIndex)
                
                #the row value is set as i
                rows[i][j].row = i
                
                #the pointers for each direction are set
                rows[i][j].right = rows[i][(j+1)%4]
                rows[i][j].left = rows[i][(j+3)%4]
                rows[i][j].up = cols[columnIndex].up #point the up to the headers previous up pointer/the previous bottom of the gird
                rows[i][j].head = cols[columnIndex] #.head always stores the header for the row
                rows[i][j].up.down = rows[i][j] # make the up point down to the current cell
                rows[i][j].down = rows[i][j].head # point it to the header of the column, because it is the latest node so will be at the bottom

                cols[columnIndex].up.down = rows[i][j]
                cols[columnIndex].up = rows[i][j] #link head to cell
                cols[columnIndex].count += 1 #increment count

    #once there is a solution this function is used to return a 9x9 matrix with the correct numbers    
    def createSolution(self):
        grid = self.grid
        solution = self.solution
        solvedSudoku = self.solvedSudoku

        n = len(grid)

        #finds the corresponding row and column for the sudoku and inputs the correct number
        for row in solution:
            actualRow = row//(n*n)
            actualCol = (row//n)%n
            offset = row%n + 1
            
            solvedSudoku[actualRow][actualCol] = int(offset)

        

    #this is used to cover a column
    def cover(self, column):
        
        #delete the column from the doubly linked list
        column.right.left = column.left
        column.left.right = column.right
        
        #for each node contained in column
        currentNode = column.down
        while currentNode != column:

            #for each Node in the same row as the current node
            rowNode = currentNode.right
            while rowNode != currentNode:
                
                #remove the node from its column by pointing the node above and below it to each other
                rowNode.up.down = rowNode.down
                rowNode.down.up = rowNode.up
            
                #remove one from the count of its column head
                rowNode.head.count -= 1

                #move to next node
                rowNode = rowNode.right
                
            #move to the next node in the column    
            currentNode = currentNode.down
        
    #this is used to uncover a column when backtracking
    def uncover(self, column):

        tempColumn = column.up
        while tempColumn != column:

            tempRow = tempColumn.left
            while tempRow != tempColumn:
                
                tempRow.up.down = tempRow
                tempRow.down.up = tempRow
                tempRow.head.count += 1 

                tempRow = tempRow.left

            tempColumn = tempColumn.up
        
        column.right.left = column
        column.left.right = column

    #this is the main function for solving the sudoku
    def solveSudoku(self,depth):
        rootNode = self.rootNode
        solution = self.solution

        #if the root node points to itself then all columns have been covered and there is a solution
        if rootNode.right == rootNode:
            self.isSolved = True
            self.createSolution()
            return
        

        #This method uses a hieuristic selcetion of the best column by selecting the column with the fewest nodes
        bestCol = rootNode.right
        currentCol = rootNode.right
        while currentCol != rootNode:

            #pick the column with the lowest count
            if currentCol.count < bestCol.count:
                bestCol = currentCol

            currentCol = currentCol.right

        

        #cover the selected column
        self.cover(bestCol)
        
        #for each Node in the covered column, move along the row and cover the columns of any other Nodes present in the column
        currentRow = bestCol.down
        while currentRow != bestCol:
            
            #add the current row to the solution
            if depth<len(solution):
                solution.pop(depth)

            solution.insert(depth, currentRow.row)

            #move right, covering the columns of any node
            tempNode = currentRow.right
            while tempNode != currentRow:
            
                
                self.cover(tempNode.head)
                
                tempNode = tempNode.right
            
            #continue to call
            self.solveSudoku(depth+1)

        
            #if no solution is found, then pop the row from the solution
            solution.pop(depth)

            #now everything is uncovered in the reverse way that it was covered
            tempNode = currentRow.left
            while tempNode != currentRow:

                self.uncover(tempNode.head)

                tempNode = tempNode.left


            currentRow = currentRow.down
        self.uncover(bestCol)

#this is the main function which takes a sudoku as a 9x9 np array and returns its solution or a 9x9 array of -1 if there is no solution
def sudoku_solver(sudoku):
    noSolution = np.array([[-1]*9]*9)
    s = Sudoku(sudoku)
    s.generateConstraintMatrix()
    s.solveSudoku(0)
    if s.isSolved:
        return s.solvedSudoku
    else:
        return noSolution

