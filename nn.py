"""
The design of this comes from here:
http://outlace.com/Reinforcement-Learning-Part-3/
"""

from keras.models import Sequential
from keras.layers.core import Dense, Activation, Dropout
from keras.optimizers import RMSprop, Adagrad
from keras.layers.recurrent import LSTM
from keras.callbacks import Callback

# Adding this per a suggestion by Tim Kelch.
# https://medium.com/@trkelch/this-post-is-great-possibly-the-best-tutorial-explanation-ive-found-thus-far-cf78886b5378#.w473ywtbw
import tensorflow as tf

class LossHistory(Callback):
    def on_train_begin(self, logs={}):
        self.losses = []

    def on_batch_end(self, batch, logs={}):
        self.losses.append(logs.get('loss'))


def neural_net(input_size, params, load=''):
    model = Sequential()

    # First layer.
    model.add(Dense(
        params['nodes1'], kernel_initializer='lecun_uniform', input_shape=(input_size,),activation='relu'
    ))
    # model.add(Activation('relu'))
    model.add(Dropout(0.2))

    if(params['nodes2']!=0):
        # Second layer.
        model.add(Dense(params['nodes2'], kernel_initializer='lecun_uniform', activation='relu'))
        model.add(Dropout(0.2))

    # Output layer.
    model.add(Dense(params['num_actions'], kernel_initializer='lecun_uniform',activation='softmax'))
    # model.add(Activation('linear'))

    solver = params['solver']

    if(solver=='rms'):
        rms = RMSprop()
        model.compile(loss='mse', optimizer=rms)
    elif(solver=='ada'):
        ada = Adagrad()
        model.compile(loss='mse', optimizer=ada)
    else:
        raise(ValueError('no solver built'))

    if load:
        model.load_weights(load)

    return model


def lstm_net(input_size, load=False):
    model = Sequential()
    model.add(LSTM(
        output_dim=512, input_dim=input_size, return_sequences=True
    ))
    model.add(Dropout(0.2))
    model.add(LSTM(output_dim=512, input_dim=512, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(output_dim=3, input_dim=512))
    model.add(Activation("linear"))
    model.compile(loss="mean_squared_error", optimizer="rmsprop")

    return model
