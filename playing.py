"""
Once a model is learned, use this to play it.
"""

from grid_game import *
import numpy as np
from nn import neural_net
import time
import pygame
from car_model import *
from lane_following import *

pygame.init()

# X_DIM, Y_DIM = (5,5)


def play_grid(model):

    grid = Grid(X_DIM, Y_DIM)
    car = Car(grid, 0, 0)
    game_state = World(grid, car, 500, 10, False)
    state = game_state.grid.getState()

    action_grid = [[0 for x in range(X_DIM)] for y in range(Y_DIM)]

    for i in range(Y_DIM):
        for j in range(X_DIM):
            fake_state = np.zeros((1, X_DIM * Y_DIM))
            k = (i * X_DIM) + j
            fake_state[0][k] = 1
            action_grid[i][j] = np.argmax(
                model.predict(fake_state, batch_size=1))

    for i in range(Y_DIM):
        line = '| '
        for j in range(X_DIM):
            if [j, i] == game_state.goal:
                line += '$ | '
            elif action_grid[i][j] == 2:
                line += 'v | '
            elif action_grid[i][j] == 1:
                line += '^ | '
            else:
                line += '> | '
        print(line)

    time.sleep(2)

    # Move.
    while True:

        # Choose action.
        action = (np.argmax(model.predict(state, batch_size=1)))

        # Take action.
        _, state = game_state.updateState(action)

        game_state.grid.printGrid()

        time.sleep(0.5)


def play_lane_following(model):
    rate = 10  # Hz
    screen = pygame.display.set_mode((1300, 600))
    pygame.display.set_caption("mdeyo car sim")
    background = pygame.Surface(screen.get_size())
    background.fill((0, 0, 0))
    RED = (255,   0,   0)
    car = Car2(RED, 60, 385, screen, 100)
    road = CurvedRoad(1200, 60, 385, '45')
    car.constant_speed = True
    state = road.getState(car)
    print('state:', state)

    # Move.
    while True:

        # Choose an action.
        action = np.argmax(model.predict(state, batch_size=1))

        # Take action, observe new state and get our treat.
        print(action)
        car.takeAction(action)
        car.update(1 / rate)
        road.plotRoad(screen)

        state = road.getState(car)
        print(state)
        (car_reward, done) = road.reward(car)
        # --- Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

        # --- Limit to 60 frames per second
        # clock.tick(rate)
        print(car_reward)

        # time.sleep(0.1)


if __name__ == "__main__":
    # saved_model = 'saved-models/5x5-82n-75n-100-50000-2000.h5'
    # model = neural_net(25, [82, 75], saved_model)
    # play_grid(model)

    nn = [164, 41]
    num_input = 3

    saved_model = 'saved-models/lane_following-' + \
        str(nn[0]) + 'n-' + str(nn[1]) + \
        'n-10000frames-50-50000buffer-rms-6000.h5'
    params = {
        'nodes1': nn[0],
        'nodes2': nn[1],
        'x_dim': X_DIM,
        'y_dim': Y_DIM,
        "batchSize": 100,
        "buffer": 50000,
        "nn": nn,
        'solver': 'rms',
        'num_actions': 3
    }
    model = neural_net(num_input, params, saved_model)
    play_lane_following(model)
