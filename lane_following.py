
import numpy as np
import matplotlib.pyplot as plt
import pygame

# print(x)


class CurvedRoad():
    def __init__(self, length, x, y, type):
        self.cost = 0
        self.type = type
        self.start = 250
        self.x_offset = x
        self.y_offset = y
        self.length = length
        self.x = np.arange(x, length + x, 1)
        self.slope = 0.3
        if type == 'curved':
            self.y = curvedRoadY(self.x, self.start)
        elif type == '0':
            self.y = y
        elif type == '45':
            self.y = turn45(self.x, self.x_offset, self.start, self.slope)
        else:
            raise ValueError('incorrect road type given')
        self.points = list(zip(self.x, self.y_offset - self.y))

    def getY(self, x):
        if self.type == 'curved':
            return self.y_offset - paramaterizedTurn(x, self.start)
        if self.type == '45':
            return self.y_offset - paramaterizedTurn45(x, self.x_offset, self.start, self.slope)

    def scanRoad(self, car):
        # x,y = car.next_position()
        x, y = car.pose
        y_road = self.getY(x)
        distance_to_road = y - y_road
        # print('next_x',x,'next_y',y,'road_y',y_road)
        # return [x,distance_to_road,distance_to_road**2]
        # return [x, distance_to_road, car.angle]
        return distance_to_road

    def getState(self, car):
        # state = np.zeros((1,3))
        # state = np.zeros((1,2))
        state = car.updateSlidingHistory(self.scanRoad(car))
        # print(state)
        return state

    def reward(self, car):

        x, y = car.pose
        road_y = self.getY(x)

        # cost function squared distance from road at given x
        from_road_cost = -((road_y - y)**2) / 10
        from_road_cost = -((road_y - y)**2) / 100

        # cost function distance from straight line progress
        weight_progress = 5
        progress_cost = weight_progress * (x - (car.speed * car.timer))

        total_cost = from_road_cost + progress_cost

        if(car.timer > car.time_limit):
            print('****  beyond time limit ********')
            car.reset()
            final_cost = self.cost
            self.cost = 0
            # return (final_cost,1)
            return (total_cost, 1)

        elif(car.pose[0] > self.start + self.length):
            print('#####  beyond x limit ######')
            car.reset()
            final_cost = self.cost
            self.cost = 0
            # return (final_cost,1)
            return (total_cost, 1)

        self.cost += total_cost
        # print('x,y ',x,y,' road y ',road_y)
        # return (total_cost,0)
        return (total_cost, 0)

    def plotRoad(self, screen):
        # print(self.points)s
        WHITE = (255, 255, 255)
        pygame.draw.lines(screen, WHITE, False, self.points, 10)


def paramaterizedTurn(x, start):
    x1, y1, r1 = (start, 150, 150)
    x2, y2, r2 = (start + 300, 150, 150)
    x3, y3, r3 = (start + 600, 150, 150)

    if x <= x1 or x >= x3:
        return 0
    elif x > x1 and x <= (x1 + r1):
        return y1 - np.sqrt(r1**2 - (x - x1)**2)
    elif x > (x2 - r2) and x <= (x2 + r2):
        return y2 + np.sqrt(r2**2 - (x - x2)**2)
    elif x > (x3 - r3) and x <= x3:
        return y3 - np.sqrt(r3**2 - (x - x3)**2)
    else:
        return 0


def curvedRoadY(x_array, start):
    n = x_array.shape[0]

    y = np.zeros(n)
    for i in range(n):
        y[i] = (paramaterizedTurn(x_array[i], start))
        # print(laneFollowingReward(x_array[i],0))

    return y


def paramaterizedTurn45(x, offset, start, slope):
    if x < start + offset:
        return 0
    else:
        return (x - start - offset) * slope


def turn45(x_array, offset, start, slope):
    n = x_array.shape[0]
    y = np.zeros(n)
    for i in range(n):
        y[i] = paramaterizedTurn45(x_array[i], offset, start, slope)
    return y


if __name__ == "__main__":
    x = np.arange(0, 500, 1)
    print(paramaterizedTurn(301, 250))
    # y = curvedRoadY(x,5)
    y = turn45(x, 200, 0.5)

    plt.plot(x, y)
    plt.axis([0, 500, -200, 500])
    plt.show()
