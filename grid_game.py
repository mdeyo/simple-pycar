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


from nn import neural_net, LossHistory
import timeit
import random
import numpy as np


X_DIM, Y_DIM = (5, 5)


class World():
    def __init__(self, grid, car, goal_reward, step_cost):
        self.grid = grid
        self.car = car
        self.goal_reward = goal_reward
        self.step_cost = step_cost
        self.state = grid.grid

    def updateState(self, action):
        if action in self.car.getAvailableActions():
            self.car.takeAction(action)
            return(-10, self.grid.getState())

        else:  # action not avaialble - penalize -500
            return (-500, self.grid.getState())


class Grid():
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.grid = [[0 for x in range(w)] for y in range(h)]

    def getState(self):
        state = []
        for row in self.grid:
            state.extend(row)
        state = np.transpose(np.array(state))
        state = state.reshape(1, 25)
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
        grid.addCar(self)

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
        print('move Right')
        newx = self.x
        newy = self.y + 1
        if(self.grid.clear(newx, newy)):
            self.x, self.y = (newx, newy)
        else:
            print("ERROR - next position not clear")
        grid.update(self)

    def moveLeft(self):
        print('move Left')
        newx = self.x
        newy = self.y - 1
        if(self.grid.clear(newx, newy)):
            self.x, self.y = (newx, newy)
        else:
            print("ERROR - next position not clear")
        grid.update(self)

    def driveForward(self):
        print('drive forward')
        newx = self.x + 1
        newy = self.y
        if(self.grid.clear(newx, newy)):
            self.x, self.y = (newx, newy)
        else:
            print("ERROR - next position not clear")
        grid.update(self)


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


grid = Grid(X_DIM, Y_DIM)
car = Car(grid, 0, 0)

grid.printGrid()

print(grid.getState())

print(car.getAvailableActions())


NUM_INPUT = 25
GAMMA = 0.9  # Forgetting.
TUNING = False  # If False, just use arbitrary, pre-selected params.


def train_net(model, params):

    filename = params_to_filename(params)

    observe = 1000  # Number of frames to observe before training.
    epsilon = 1
    train_frames = 1000000  # Number of frames to play.
    batchSize = params['batchSize']
    buffer = params['buffer']

    # Just stuff used below.
    max_car_distance = 0
    car_distance = 0
    t = 0
    data_collect = []
    replay = []  # stores tuples of (S, A, R, S').

    loss_log = []

    # Create a new game instance.
    # game_state = carmunk.GameState()
    grid = Grid(X_DIM, Y_DIM)
    car = Car(grid, 0, 0)
    game_state = World(grid, car, 500, 10)

    # Get initial state by doing nothing and getting the state.
    #_, state = game_state.frame_step((2))
    _, state = game_state.updateState(0)

    # Let's time it.
    start_time = timeit.default_timer()

    # Run the frames.
    while t < train_frames:

        t += 1
        car_distance += 1

        # Choose an action.
        if random.random() < epsilon or t < observe:
            action = np.random.randint(0, 3)  # random
        else:
            # Get Q values for each action.
            qval = model.predict(state, batch_size=1)
            action = (np.argmax(qval))  # best

        # Take action, observe new state and get our treat.
        #reward, new_state = game_state.frame_step(action)
        reward, new_state = game_state.updateState(action)

        # Experience replay storage.
        replay.append((state, action, reward, new_state))

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
                nb_epoch=1, verbose=0, callbacks=[history]
            )
            loss_log.append(history.losses)

        # Update the starting state with S'.
        state = new_state

        # Decrement epsilon over time.
        if epsilon > 0.1 and t > observe:
            epsilon -= (1 / train_frames)

        # We died, so update stuff.
        if reward == -500:
            # Log the car's distance at this T.
            data_collect.append([t, car_distance])

            # Update max.
            if car_distance > max_car_distance:
                max_car_distance = car_distance

            # Time it.
            tot_time = timeit.default_timer() - start_time
            fps = car_distance / tot_time

            # Output some stuff so we can watch.
            print("Max: %d at %d\tepsilon %f\t(%d)\t%f fps" %
                  (max_car_distance, t, epsilon, car_distance, fps))

            # Reset.
            car_distance = 0
            start_time = timeit.default_timer()

        # Save the model every 25,000 frames.
        if t % 25000 == 0:
            model.save_weights('saved-models/' + filename + '-' +
                               str(t) + '.h5',
                               overwrite=True)
            print("Saving model %s - %d" % (filename, t))

    # Log results after we're done all frames.
    log_results(filename, data_collect, loss_log)


def log_results(filename, data_collect, loss_log):
    # Save the results to a file so we can graph it later.
    with open('results/sonar-frames/learn_data-' + filename + '.csv', 'w') as data_dump:
        wr = csv.writer(data_dump)
        wr.writerows(data_collect)

    with open('results/sonar-frames/loss_data-' + filename + '.csv', 'w') as lf:
        wr = csv.writer(lf)
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
        # print(new_state_m)

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
        y[0][action_m] = update
        X_train.append(old_state_m.reshape(NUM_INPUT,))
        y_train.append(y.reshape(3,))

    X_train = np.array(X_train)
    y_train = np.array(y_train)

    return X_train, y_train


def params_to_filename(params):
    return str(params['nn'][0]) + '-' + str(params['nn'][1]) + '-' + \
        str(params['batchSize']) + '-' + str(params['buffer'])


def launch_learn(params):
    filename = params_to_filename(params)
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
    params = {
        "batchSize": 100,
        "buffer": 50000,
        "nn": nn_param
    }
    model = neural_net(NUM_INPUT, nn_param)
    train_net(model, params)
