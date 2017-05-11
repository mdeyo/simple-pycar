# Dumbed down version of car simulator
# For first tests of Q-learning techniques

# 5x5 grid world
# Our car starts in one of the 10 blocks in the left-most 2 columns
# There are two or three red squares with a reward of -10 (obstacles)
# There is a region on the right-most side with reward 10
# Our car can take one of 3 actions each turn:
#   drive straight - car moves one square forward
#   drive left
#   drive right


import random
import numpy as np


X_DIM, Y_DIM = (5, 5)


class World():
    def __init__(self, grid, car, goal_reward, step_cost, printing):
        self.grid = grid
        self.car = car
        self.goal_reward = goal_reward
        self.step_cost = step_cost
        self.state = grid.grid
        self.cost = 0
        self.goal = [X_DIM-1,2]
        self.printing = printing
        self.car.printing = printing
        self.grid.printing = printing

    def updateState(self, action):

        try:
            if(self.cost==-self.goal_reward):
                self.restartGame()
                return (-500,self.grid.getState())
            action = int(action)
            
            if action in self.car.getAvailableActions():
                if self.printing:
                    print('taking action: '+str(action))
                self.car.takeAction(action)

                if self.printing:
                    self.grid.printGrid()
                if self.checkGoal():
                    reward = self.cost + self.goal_reward - self.step_cost
                    print('## reached goal with reward: ',reward,' ##')
                    self.restartGame()
                    return(reward,self.grid.getState())
                else:
                    self.cost -= self.step_cost
                    return(self.cost, self.grid.getState())

            else:  # action not available - penalize -500
                if self.printing:
                    print('not in available actions')
                # self.restartGame()
                # self.cost -= self.step_cost
                # return(self.cost, self.grid.getState())
                return (-500, self.grid.getState())

        except ValueError as e:
            print('input value error')
            return(0,0)



    def checkGoal(self):
        if self.car.x == self.goal[0] and self.car.y == self.goal[1]:
            if self.printing:
                print('reached goal!')
            return True
        return False

    def restartGame(self):

        self.grid = Grid(self.grid.w, self.grid.h)
        self.car = Car(self.grid,0,random.randint(0,self.grid.h-1))
        self.state = self.grid.grid
        self.cost = 0
        self.goal = [4,2]


class Grid():
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.state_length = w*h
        self.grid = [[0 for x in range(w)] for y in range(h)]

    def getGrid(self):
        return self.grid.copy()

    def getState(self):
        state = []
        for row in self.grid:
            state.extend(row)
        state = np.transpose(np.array(state))
        state = state.reshape(1, self.state_length)
        # print(state.shape)
        return state

    def addCar(self, car):
        self.car = car
        self.grid[car.y][car.x] = 1
        self.carPos = (car.x, car.y)

    def update(self, car):
        self.grid[self.carPos[1]][self.carPos[0]] = 0
        self.grid[car.y][car.x] = 1
        self.carPos = (car.x, car.y)

    def clear(self, x, y):
        if x < 0 or y < 0:
            return False
        try:
            b = self.grid[y][x]
            if(b == 0):
                return True
            return False
        except IndexError:
            return False

    def printGrid(self):
        printDivide()
        for i in range(self.w):
            line = ' '
            for j in range(self.h):
                if (j, i) == self.carPos:
                    line += '[ ]'
                else:
                    line += ' 0 '
            print(line)

        # for i in self.grid:
            # print(i)
        printDivide()


class Car():
    def __init__(self, grid, x, y):
        self.x = x
        self.y = y
        self.grid = grid
        self.grid.addCar(self)
        self.printing = False #default value

    def getAvailableActions(self):
        actions = []
        if(self.grid.clear(self.x + 1, self.y)):
            actions.append(0)
        if(self.grid.clear(self.x, self.y - 1)):
            actions.append(1)
        if(self.grid.clear(self.x, self.y + 1)):
            actions.append(2)
        return actions

    def takeAction(self, action):
        if action == 0:
            self.driveForward()
        elif action == 1:
            self.moveLeft()
        elif action == 2:
            self.moveRight()

    def moveRight(self):
        if self.printing:
            print('move Right')
        newx = self.x
        newy = self.y + 1
        if(self.grid.clear(newx, newy)):
            self.x, self.y = (newx, newy)
        else:
            print("ERROR - next position not clear")
        self.grid.update(self)

    def moveLeft(self):
        if self.printing:
            print('move Left')
        newx = self.x
        newy = self.y - 1
        if(self.grid.clear(newx, newy)):
            self.x, self.y = (newx, newy)
        else:
            print("ERROR - next position not clear")
        self.grid.update(self)

    def driveForward(self):
        if self.printing:
            print('drive forward')
        newx = self.x + 1
        newy = self.y
        if(self.grid.clear(newx, newy)):
            self.x, self.y = (newx, newy)
        else:
            print("ERROR - next position not clear")
        self.grid.update(self)


def printDivide():
    print('***********')


def printGrid(grid):
    printDivide()
    for row in grid:
        line = ' '
        for i in row:
            line += str(i) + ' '
        print(line)
    printDivide()





if __name__ == "__main__":
    grid = Grid(X_DIM, Y_DIM)
    car = Car(grid, 0, 0)

    grid.printGrid()

    print(grid.getState())

    print(car.getAvailableActions())

    game_state = World(grid, car, 500, 10)


    gameMode = True

    while gameMode:
        cmd = input("Next action? [0,1,2] \n")
        s,c = game_state.updateState(cmd)
        print(s)
        print(c)
