

from nn import neural_net, LossHistory
import timeit
import random
import numpy as np
import csv
from grid_game import *
from playing import *
import pygame
from car_model import *
from lane_following import *
import os

pygame.init()

# X_DIM, Y_DIM = (5, 5)
NUM_INPUT = X_DIM * Y_DIM
NUM_INPUT = 3
NUM_INPUT = 10

GAMMA = 0.9  # Forgetting.
TUNING = False  # If False, just use arbitrary, pre-selected params.
TRAIN_FRAMES = 10000  # Number of frames to play.


def check_folders():
    directory_names = ["saved-models", "results"]
    for directory in directory_names:
        if not os.path.exists(directory):
            os.makedirs(directory)


def train_net(model, params, mode='grid'):

    observe = 1000  # Number of frames to observe before training.
    epsilon = 1
    train_frames = 10000  # Number of frames to play.
    train_frames = TRAIN_FRAMES

    filename = params_to_filename(params, mode, train_frames)
    print(filename)

    if mode == 'lane_following':
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

    if mode == 'grid':
        # Create a new game instance.
        # game_state = carmunk.GameState()
        grid = Grid(X_DIM, Y_DIM)
        car = Car(grid, 0, 0)
        game_state = World(grid, car, 500, 10, False)
        # Get initial state by doing nothing and getting the state.
        _, state = game_state.updateState(0)

    batchSize = params['batchSize']
    buffer = params['buffer']

    # Just stuff used below.
    max_car_reward = -999999
    car_reward = 0
    t = 0
    data_collect = []
    replay = []  # stores tuples of (S, A, R, S')
    loss_log = []

    # Let's time it.
    start_time = timeit.default_timer()

    # Run the frames.
    while t < train_frames:

        t += 1

        if mode == 'grid':
            # Choose an action.
            if random.random() < epsilon or t < observe:
                action = np.random.randint(0, 3)  # random
            else:
                # Get Q values for each action.
                qval = model.predict(state, batch_size=1)
                action = (np.argmax(qval))  # best

            # Take action, observe new state and get our treat.
            #reward, new_state = game_state.frame_step(action)
            car_reward, new_state = game_state.updateState(action)
            # car_reward = reward
            # print(reward)

        elif mode == 'lane_following':
            # Choose an action.
            if random.random() < epsilon or t < observe:
                action = np.random.randint(0, 3)  # random
                # actions currently are 0 = no input (drive straight)
                #                       1 = left turn input
                #                       2 = right turn input
            else:
                # Get Q values for each action.
                qval = model.predict(state, batch_size=1)
                action = (np.argmax(qval))  # best

            # Take action, observe new state and get our treat.
            # print(action)
            car.takeAction(action)
            car.update(1 / rate)
            road.plotRoad(screen)

            new_state = road.getState(car)
            (car_reward, done) = road.reward(car)

            # --- Go ahead and update the screen with what we've drawn.
            pygame.display.flip()

            # --- Limit to 60 frames per second
            # clock.tick(rate)
            # print(car_reward)

        # Experience replay storage.
        print(t, 'reward', car_reward)
        # print('state:', state, 'action', action, 'reward',
        #       car_reward, 'new_state', new_state)
        replay.append((state, action, car_reward, new_state))

        # If we're done observing, start training.
        if t > observe:

            # If we've stored enough in our buffer, pop the oldest.
            if len(replay) > buffer:
                replay.pop(0)

            # Randomly sample our experience replay memory
            minibatch = random.sample(replay, batchSize)

            # Get training values.
            X_train, y_train = process_minibatch(minibatch, model)

            # Train the model on this batch.
            history = LossHistory()
            model.fit(
                X_train, y_train, batch_size=batchSize,
                epochs=1, verbose=0, callbacks=[history]
            )
            loss_log.append(history.losses)

        # Update the starting state with S'.
        state = new_state

        # print(state)
        # game_state.grid.printGrid()
        # print(reward)

        # Decrement epsilon over time.
        if epsilon > 0.1 and t > observe:
            epsilon -= (1 / train_frames)

        # We died, so update stuff.
        if done == 1:
            # if reward > 0 or reward==-999:
            # Log the car's distance at this T.
            data_collect.append([t, car_reward])

            # Update max.
            if car_reward > max_car_reward:
                max_car_reward = car_reward

            # Time it.
            tot_time = timeit.default_timer() - start_time
            # fps = car_distance / tot_time

            # Output some stuff so we can watch.
            print("Max: %d at %d\tepsilon %f\t(%d)\t" %
                  (max_car_reward, t, epsilon, car_reward))

            # Reset.
            car_reward = 0
            start_time = timeit.default_timer()

        # Save the model every 25,000 frames.
        if t % 100 == 0:
            print(t)
        if t % 2000 == 0:
            model.save_weights('saved-models/' + filename + '-' +
                               str(t) + '.h5',
                               overwrite=True)
            print("Saving model %s - %d" % (filename, t))

    # Log results after we're done all frames.
    print(train_frames)
    log_results(filename, data_collect, loss_log, train_frames, observe)


def log_results(filename, data_collect, loss_log, train_frames, observe):
    # Save the results to a file so we can graph it later.
    with open('results/learn_data-' + filename + '.csv', 'w') as data_dump:
        wr = csv.writer(data_dump)
        wr.writerow(['train_frames', train_frames])
        wr.writerow(['observe', observe])
        wr.writerows(data_collect)

    with open('results/loss_data-' + filename + '.csv', 'w') as lf:
        wr = csv.writer(lf)
        wr.writerow(['train_frames', train_frames])
        wr.writerow(['observe', observe])
        for loss_item in loss_log:
            wr.writerow(loss_item)


def process_minibatch(minibatch, model):
    """This does the heavy lifting, aka, the training. It's super jacked."""
    X_train = []
    y_train = []
    # Loop through our batch and create arrays for X and y
    # so that we can fit our model at every step.
    for memory in minibatch:
        # Get stored values.
        old_state_m, action_m, reward_m, new_state_m = memory
        # print('old_state_m:')
        # print(old_state_m)
        # print('action_m:')
        # print(action_m)
        # print(reward_m)
        # print(new_state_m)'
        # print(old_state_m,action_m,reward_m,new_state_m)

        # Get prediction on old state.
        old_qval = model.predict(old_state_m, batch_size=1)
        # Get prediction on new state.
        newQ = model.predict(new_state_m, batch_size=1)
        # Get our best move. I think?
        maxQ = np.max(newQ)
        y = np.zeros((1, 3))
        y[:] = old_qval[:]
        # Check for terminal state.
        if reward_m != -500:  # non-terminal state
            update = (reward_m + (GAMMA * maxQ))
        else:  # terminal state
            update = reward_m
        # Update the value for the action we took.
        # print(update)
        y[0][action_m] = update
        X_train.append(old_state_m.reshape(NUM_INPUT,))
        y_train.append(y.reshape(3,))

    X_train = np.array(X_train)
    y_train = np.array(y_train)

    return X_train, y_train


def params_to_filename(params, mode, train_frames):
    if mode == 'grid':
        return str(params['x_dim']) + 'x' + str(params['y_dim']) + '-' + str(params['nn'][0]) + 'n-' + str(params['nn'][1]) + 'n-' + str(train_frames) + 'frames-' + \
            str(params['batchSize']) + '-' + str(params['buffer']) + \
            'buffer-' + str(params['solver'])
    elif mode == 'lane_following':
        return 'lane_following' + '-' + str(params['nn'][0]) + 'n-' + str(params['nn'][1]) + 'n-' + str(train_frames) + 'frames-' + \
            str(params['batchSize']) + '-' + str(params['buffer']) + \
            'buffer-' + str(params['solver'])


def launch_learn(params):
    filename = params_to_filename(params, TRAIN_FRAMES)
    print("Trying %s" % filename)
    # Make sure we haven't run this one.
    if not os.path.isfile('results/sonar-frames/loss_data-' + filename + '.csv'):
        # Create file so we don't double test when we run multiple
        # instances of the script at the same time.
        open('results/sonar-frames/loss_data-' + filename + '.csv', 'a').close()
        print("Starting test.")
        # Train.
        model = neural_net(NUM_INPUT, params['nn'])
        train_net(model, params)
    else:
        print("Already tested.")


if __name__ == "__main__":

    check_folders()

    # if TUNING:
    #     param_list = []
    #     nn_params = [[164, 150], [256, 256],
    #                  [512, 512], [1000, 1000]]
    #     batchSizes = [40, 100, 400]
    #     buffers = [10000, 50000]
    #
    #     for nn_param in nn_params:
    #         for batchSize in batchSizes:
    #             for buffer in buffers:
    #                 params = {
    #                     "batchSize": batchSize,
    #                     "buffer": buffer,
    #                     "nn": nn_param
    #                 }
    #                 param_list.append(params)
    #
    #     for param_set in param_list:
    #         launch_learn(param_set)
    #
    # else:
    nn_param = [164, 150]
    nn_param = [164, 0]
    nn_param = [64, 32]

    nn_param = [12, 8]
    nn_param = [164, 41]

    params = {
        'nodes1': nn_param[0],
        'nodes2': nn_param[1],
        'x_dim': X_DIM,
        'y_dim': Y_DIM,
        "batchSize": 50,
        "buffer": 50000,
        "nn": nn_param,
        'solver': 'rms',
        'num_actions': 3
    }
    model = neural_net(NUM_INPUT, params)
    print('made model')
    train_net(model, params, 'lane_following')

    play_lane_following(model)

    # play(model)
