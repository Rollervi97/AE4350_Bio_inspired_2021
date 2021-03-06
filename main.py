# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import matplotlib.pyplot as plt
import keras.optimizers
import tensorflow as tf
from numpy import loadtxt
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, LSTM, Input
from keras.models import model_from_json
import os, sys
import numpy as np
import levenberg_marquardt as lm
from keras.optimizers import SGD
from datetime import datetime

dataset_number = 0


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def getfilelist(path):
    file_list = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    opti_file = []
    cfsd_file = []

    for item in file_list:
        if len(item) >= 4:
            if item[:4] == 'opti':
                opti_file.append(item)
            elif item[:4] == 'cfsd':
                cfsd_file.append(item)

    return file_list, opti_file, cfsd_file


def getFFNNmodel(input_dim, out_dim):
    model = Sequential()
    model.add(Dense(80, input_shape=input_dim, activation='relu', use_bias=True))
    model.add(Dropout(0.1))
    model.add(Dense(60, activation=None))
    model.add(Dropout(0.1))
    model.add(Dense(40, activation='sigmoid'))
    model.add(Dropout(0.1))
    model.add(Dense(25, activation='tanh'))
    model.add(Dropout(0.1))
    model.add(Dense(out_dim[0], activation=None))
    print(model.summary())
    return model


def getRNNmodel(input_dim, out_dim):
    model = Sequential()
    model.add(Dense(80, input_shape=input_dim, activation='relu', use_bias=True))
    model.add(Dropout(0.1))
    model.add(Dense(60, activation=None))
    model.add(Dropout(0.1))
    model.add(Dense(40, activation='sigmoid'))
    model.add(Dropout(0.1))
    model.add(Dense(25, activation='tanh'))
    model.add(Dropout(0.1))
    model.add(LSTM(25, activation='tanh'))
    model.add(Dropout(0.1))
    model.add(Dense(out_dim[0], activation=None))
    print(model.summary())
    return model


def trainmodel(m, input, target, input_v, target_v, ep, b_size):
    m.fit(input, target, epochs=ep, batch_size=b_size, validation_data=(input_v, target_v))
    return m


def savew(m, path):
    m.save_weights(path, overwrite=True)


def loadw(m, path):
    m.load_weights(path)
    return m


def testmain(sp):
    data_path = 'C:/Users/ASUS/Google Drive/TU Delft/AE4350_Bio_inspired_intelligence_and_learning_for_Aerospace_Application/flight_data/csv_data'
    [fl, opti_file, cfsd_file] = getfilelist(data_path)
    #

    data = loadtxt(f"{data_path}/{cfsd_file[dataset_number]}", delimiter=',')  # numpy array
    gt = loadtxt(f"{data_path}/{opti_file[dataset_number]}", delimiter=',')  # numpy array

    training = data[:, :12]  #

    ekf_x = data[:, 17]
    ekf_y = data[:, 18]
    ekf_z = data[:, 19]
    ekf_pitch = data[:, 13]
    ekf_roll = data[:, 14]
    ekf_yaw = data[:, 16]

    ekf = [ekf_x, ekf_y, ekf_z, ekf_roll, ekf_pitch, ekf_yaw]

    gt_x = gt[:, 0]
    gt_y = gt[:, 1]
    gt_z = gt[:, 2]
    gt_pitch = gt[:, 3]
    gt_roll = gt[:, 4]
    gt_yaw = gt[:, 5]
    name = ["pos x", "pos y", "pos z", "att roll", "att pitch", "att yaw"]
    n = []
    for i in range(len(name)):
        n.append(f"ds{dataset_number}_{name[i]}")

    gt_ = [gt_x, gt_y, gt_z, gt_roll, gt_pitch, gt_yaw]

    for i in range(len(gt_)):
        plt.figure()
        plt.plot(ekf[i], label=f"{name[i]} kalman filter")
        plt.plot(gt_[i], label=f"{name[i]} ground truth")
        plt.ylabel(name[i])
        plt.legend()
        plt.savefig(os.path.join(sp, n[i]))
        # plt.show()
        plt.close()

    plt.figure()
    plt.plot
    # plt.figure()
    # plt.plot(data[:,])
    # for i in range(100):
    #     print(int(np.floor(15 * np.random.rand(1)[0])))
    print("end")


def evaluate_network(sp):
    data_path = 'C:/Users/ASUS/Google Drive/TU Delft/AE4350_Bio_inspired_intelligence_and_learning_for_Aerospace_Application/flight_data/csv_data'
    [fl, opti_file, cfsd_file] = getfilelist(data_path)

    jf = open("RNN_model.json", "r")
    RNN = jf.read()
    jf.close()
    RNN = model_from_json(RNN)
    RNN.load_weights("RNN_weights.h5")

    jf = open("FFNN_model.json", "r")
    FFNN = jf.read()
    jf.close()
    FFNN = model_from_json(FFNN)
    FFNN.load_weights("FFNN_weights.h5")

    loss_possibilities = ['binary_crossentropy', 'sparse_categorical_crossentropy', 'mean_squared_error',
                          lm.SparseCategoricalCrossentropy()]
    optimizer_possibilities = ['adam', tf.keras.optimizers.Adam(learning_rate=0.001, decay=1e-5),
                               keras.optimizers.SGD(learning_rate=0.01, momentum=0.9)]
    metrics_possibilities = ['accuracy', keras.metrics.MeanSquaredError()]
    # compile the network
    loss_ = loss_possibilities[2]
    optimizer_ = optimizer_possibilities[1]
    metrics_ = metrics_possibilities[1]

    RNN.compile(loss=loss_, optimizer=optimizer_, metrics=metrics_)
    FFNN.compile(loss=loss_, optimizer=optimizer_, metrics=metrics_)

    index = 2

    test_input = loadtxt(f"{data_path}/{cfsd_file[index]}", delimiter=',')  # numpy array
    test_target = loadtxt(f"{data_path}/{opti_file[index]}", delimiter=',')  # numpy array

    # measurement and previous ekf data to opti track
    test_input = test_input[:, np.r_[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 16, 17, 18, 19]]
    # split in measurement and ekf
    mea_input = test_input[1:, :-6]
    # kalman = test_input[:-1, -6:]
    kalman2 = test_input[1:, -6:]

    kalman2 = np.hstack((kalman2[:, 3].reshape((kalman2.shape[0], 1)), kalman2[:, 4].reshape((kalman2.shape[0], 1)),
                         kalman2[:, 5].reshape((kalman2.shape[0], 1)), kalman2[:, 0].reshape((kalman2.shape[0], 1)),
                         kalman2[:, 1].reshape((kalman2.shape[0], 1)), kalman2[:, 2].reshape((kalman2.shape[0], 1))))

    kalman_ta = np.hstack((kalman2[0, 0] * np.ones(shape=(kalman2.shape[0], 1)),
                           kalman2[0, 1] * np.ones(shape=(kalman2.shape[0], 1)),
                           kalman2[0, 2] * np.ones(shape=(kalman2.shape[0], 1)),
                           kalman2[0, 3] * np.ones(shape=(kalman2.shape[0], 1)),
                           kalman2[0, 4] * np.ones(shape=(kalman2.shape[0], 1)),
                           kalman2[0, 5] * np.ones(shape=(kalman2.shape[0], 1))))
    kalman2 = kalman2 - kalman_ta
    # target is the error between the kalman filter and the ground truth
    # test_target = test_target[1:, :] - kalman2

    target_ta = np.hstack((test_target[0, 0] * np.ones(shape=(test_target.shape[0], 1)),
                           test_target[0, 1] * np.ones(shape=(test_target.shape[0], 1)),
                           test_target[0, 2] * np.ones(shape=(test_target.shape[0], 1)),
                           test_target[0, 3] * np.ones(shape=(test_target.shape[0], 1)),
                           test_target[0, 4] * np.ones(shape=(test_target.shape[0], 1)),
                           test_target[0, 5] * np.ones(shape=(test_target.shape[0], 1))))

    test_target = test_target - target_ta
    # test_input = np.hstack((mea_input, kalman2))
    test_input = mea_input
    v_sample = np.linspace(0, int(test_input.shape[0] - 1), int(test_input.shape[0] / 5))

    # test_input = test_input[:, np.r_[:12, 13:20]]
    # only ekf data to optitrack data
    # test_input = test_input[:, np.r_[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 11, 14, 16, 17, 18, 19]]
    yax = np.linspace(start=0, stop=test_input[:, 1].size - 1, num=test_input[:, 1].size) / 1000
    yax = yax[np.r_[v_sample.astype(int)]]
    test_input = test_input[np.r_[v_sample.astype(int)], :]
    test_target = test_target[np.r_[v_sample.astype(int)], :]

    print(f"data size = {test_input.shape}")
    #     get prediction from the neural network thing
    #     RNN_prediction = np.array()
    #     FFNN_prediction = np.array()
    flag_f = True

    for i in range(test_input.shape[0]):
        sample = test_input[i, :]
        sample = sample.reshape((1, 1, sample.size))
        if np.mod(i + 1, int(test_input.shape[0] / 10)) == 0:
            print(f"iteration {i + 1}/{test_input.shape[0]}")
        if flag_f:
            RNN_prediction = RNN.predict(sample)[0, :]
            FFNN_prediction = FFNN.predict(sample)[0, 0, :]
            flag_f = False
        else:
            RNN_prediction = np.vstack((RNN_prediction, RNN.predict(sample)[0, :]))
            FFNN_prediction = np.vstack((FFNN_prediction, FFNN.predict(sample)[0, :]))
        #
        # RNN_prediction = RNN.predict(sample)
        # FFNN_prediction = FFNN.predict(sample)
        # print(sample)
        # print(RNN_prediction)
        # print(FFNN_prediction)
        # print(test_target[i, :])
    label_list = ['position x [m]', 'position y [m]', 'position z [m]', 'roll', 'pitch', 'yaw']
    namelist = ['x_pos', 'y_pos', 'z_pos', 'roll', 'pitch_', 'yaw']
    kalman2 = kalman2[np.r_[v_sample.astype(int)], :]

    print("saving graphs")
    for i in range(RNN_prediction.shape[1]):
        print(f"graph {1 + i} / 6")
        plt.figure()
        plt.plot(yax, test_target[:, i], label="optitrack state estimation")
        plt.plot(yax, kalman2[:, i], label="Kalman filter est")
        plt.plot(yax, RNN_prediction[:, i], label="RNN prediction")
        plt.plot(yax, FFNN_prediction[:, i], label="FFNN prediction")
        plt.ylabel(label_list[i])
        plt.xlabel("Time [s]")
        plt.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left", mode="expand", borderaxespad=0, ncol=2)
        plt.savefig(f"{sp}/{namelist[i]}.png")
        plt.close()

    print("end model test")


def main(inputsize, outputsize, sp):
    data_path = 'C:/Users/ASUS/Google Drive/TU Delft/AE4350_Bio_inspired_intelligence_and_learning_for_Aerospace_Application/flight_data/csv_data'

    [fl, opti_file, cfsd_file] = getfilelist(data_path)
    # get models

    RNN = getRNNmodel(inputsize, outputsize)
    path_RNN_w = "weight_RNN_w"
    path_FFNN_w = "weight_FFNN_w"
    FFNN = getFFNNmodel(inputsize, outputsize)

    loss_possibilities = ['binary_crossentropy', 'sparse_categorical_crossentropy', 'mean_squared_error',
                          lm.SparseCategoricalCrossentropy()]
    optimizer_possibilities = ['adam', tf.keras.optimizers.Adam(learning_rate=0.001, decay=1e-5),
                               SGD(learning_rate=0.01, momentum=0.9)]
    metrics_possibilities = ['accuracy', keras.metrics.MeanSquaredError()]
    # compile the network
    loss_ = loss_possibilities[2]
    optimizer_ = optimizer_possibilities[1]
    metrics_ = metrics_possibilities[1]

    # RNN.compile(loss=loss_, optimizer=SGD(learning_rate=0.01, momentum=0.9), metrics=['accuracy'])
    # FFNN.compile(loss=loss_, optimizer=SGD(learning_rate=0.01, momentum=0.9), metrics=['accuracy'])

    RNN.compile(loss=loss_, optimizer=optimizer_, metrics=metrics_)
    FFNN.compile(loss=loss_, optimizer=optimizer_, metrics=metrics_)

    if len(opti_file) == len(cfsd_file):

        for i in range(len(cfsd_file)):
            data = loadtxt(f"{data_path}/{cfsd_file[i]}", delimiter=',')  # numpy array - cfsd
            target_ = loadtxt(f"{data_path}/{opti_file[i]}", delimiter=',')  # numpy array - optitrack

            # split data in training and validation
            # data = data[:, np.r_[:12, 13:20]]

            # only ekf data to optitrack data
            # data = data[:, np.r_[0, 13, 14, 16, 17, 18, 19]]

            # measurement and previous ekf data to opti track
            data = data[:, np.r_[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 11, 14, 16, 17, 18, 19]]
            # split in measurement and ekf
            mes = data[1:, :-6]

            kalman = data[1:, -6:]
            kalman2 = data[1:, -6:]

            kalman_ta = np.hstack((kalman2[0, 0] * np.ones(shape=(kalman2.shape[0], 1)),
                                   kalman2[0, 1] * np.ones(shape=(kalman2.shape[0], 1)),
                                   kalman2[0, 2] * np.ones(shape=(kalman2.shape[0], 1)),
                                   kalman2[0, 3] * np.ones(shape=(kalman2.shape[0], 1)),
                                   kalman2[0, 4] * np.ones(shape=(kalman2.shape[0], 1)),
                                   kalman2[0, 5] * np.ones(shape=(kalman2.shape[0], 1))))

            kalman2 = np.hstack((kalman2[:, 3].reshape((kalman2.shape[0], 1)),
                                 kalman2[:, 4].reshape((kalman2.shape[0], 1)),
                                 kalman2[:, 5].reshape((kalman2.shape[0], 1)),
                                 kalman2[:, 1].reshape((kalman2.shape[0], 1)),
                                 kalman2[:, 0].reshape((kalman2.shape[0], 1)),
                                 kalman2[:, 2].reshape((kalman2.shape[0], 1))))
            data = np.hstack((mes, kalman - kalman_ta))
            data = mes
            # target is the error between the kalman filter and the ground truth
            # target_ = target_[1:, :] - kalman2
            target_ = target_[1:, :]
            target_ta = np.hstack((target_[0, 0] * np.ones(shape=(target_.shape[0], 1)),
                                   target_[0, 1] * np.ones(shape=(target_.shape[0], 1)),
                                   target_[0, 2] * np.ones(shape=(target_.shape[0], 1)),
                                   target_[0, 3] * np.ones(shape=(target_.shape[0], 1)),
                                   target_[0, 4] * np.ones(shape=(target_.shape[0], 1)),
                                   target_[0, 5] * np.ones(shape=(target_.shape[0], 1))))
            target_ = target_ - target_ta

            data_t = data[:int(0.8 * data.shape[0]), :]
            data_v = data[int(0.8 * data.shape[0]):, :]

            # target_ = target_[1:, :]
            target_t = target_[:int(0.8 * target_.shape[0]), :]
            target_v = target_[int(0.8 * target_.shape[0]):, :]

            # reshaping the arrays to the proper format
            data_t = data_t.reshape((data_t.shape[0], 1, data_t.shape[1]))
            data_v = data_v.reshape((data_v.shape[0], 1, data_v.shape[1]))

            target_t = target_t.reshape((target_t.shape[0], 1, target_t.shape[1]))
            target_v = target_v.reshape((target_v.shape[0], 1, target_v.shape[1]))

            # train the network
            print(f"training recurrent neural network \n input shape {inputsize} - output size {outputsize}",
                  f"\n input data size {data_t.shape} ---- target data shape {target_t.shape}",
                  f"\n input data size {data_v.shape} ---- target data shape {target_v.shape}")
            RNN = trainmodel(RNN, data_t, target_t, data_v, target_v, 20, 500)
            print("training feed forward neural network")
            FFNN = trainmodel(FFNN, data_t, target_t, data_v, target_v, 20, 500)
            # save network weights
            # savew(RNN, path_RNN_w)
            # savew(FFNN, path_FFNN_w)
            #
            # #load network weights
            # RNN = loadw(RNN, path_RNN_w)
            # FFNN = loadw(FFNN, path_FFNN_w)

            RNN_json = RNN.to_json()
            with open("RNN_model.json", "w") as json_file:
                json_file.write(RNN_json)
            RNN.save_weights("RNN_weights.h5")

            FFNN_json = FFNN.to_json()
            with open("FFNN_model.json", "w") as json_file:
                json_file.write(FFNN_json)
            FFNN.save_weights("FFNN_weights.h5")

            jf = open("RNN_model.json", "r")
            RNN = jf.read()
            jf.close()
            RNN = model_from_json(RNN)
            RNN.load_weights("RNN_weights.h5")

            jf = open("FFNN_model.json", "r")
            FFNN = jf.read()
            jf.close()
            FFNN = model_from_json(FFNN)
            FFNN.load_weights("FFNN_weights.h5")

            RNN.compile(loss=loss_, optimizer=optimizer_, metrics=metrics_)
            FFNN.compile(loss=loss_, optimizer=optimizer_, metrics=metrics_)

    RNN_json = RNN.to_json()
    with open(f"{sp}/RNN_model.json", "w") as json_file:
        json_file.write(RNN_json)
    RNN.save_weights(f"{sp}/RNN_weights.h5")

    FFNN_json = FFNN.to_json()
    with open(f"{sp}/FFNN_model.json", "w") as json_file:
        json_file.write(FFNN_json)
    FFNN.save_weights(f"{sp}/FFNN_weights.h5")

    #
    # data = loadtxt(f"{data_path}/{cfsd_file[0]}", delimiter=',')  # numpy array
    # target = loadtxt(f"{data_path}/{opti_file[0]}", delimiter=',')  # numpy array
    #
    # for i in range(1, len(cfsd_file)):
    #     data = np.vstack((data, loadtxt(f"{data_path}/{cfsd_file[i]}", delimiter=',')))
    #     target = np.vstack((target, loadtxt(f"{data_path}/{opti_file[i]}", delimiter=',')))
    #
    #     training = data[:, :12]  #
    #     training = training.reshape((training.shape[0], 1, training.shape[1]))
    #
    #     ekf_target = data[:, 13:-1]  # pitch, roll, thrust, yaw, position
    #     ekf_target = ekf_target.reshape((ekf_target.shape[0], 1, ekf_target.shape[1]))
    #
    #     target = target.reshape((target.shape[0], 1, target.shape[1]))
    #
    #
    #
    # training = data[:, :12]  #
    # training = training.reshape((training.shape[0], 1, training.shape[1]))
    #
    # ekf_target = data[:, 13:-1]  # pitch, roll, thrust, yaw, position
    # ekf_target = ekf_target.reshape((ekf_target.shape[0], 1, ekf_target.shape[1]))
    #
    #
    # target =target.reshape((target.shape[0], 1, target.shape[1]))
    #
    # val_data = loadtxt(f"{data_path}/{cfsd_file[1]}", delimiter=',')  # numpy array
    #
    # val_inp = val_data[:, :12]
    # val_inp = val_inp.reshape((val_inp.shape[0], 1, val_inp.shape[1]))
    #
    # val_ekf = val_data[:, 13:-1]
    # val_ekf = val_ekf.reshape((val_ekf.shape[0], 1, val_ekf.shape[1]))
    #
    # val_out = loadtxt(f"{data_path}/{opti_file[1]}", delimiter=',')  # numpy array
    # val_out = val_out.reshape((val_out.shape[0], 1, val_out.shape[1]))
    #
    # test_data = loadtxt(f"{data_path}/{cfsd_file[2]}", delimiter=',')  # numpy array
    #
    # test_inp = test_data[:, :12]
    # test_inp = test_inp.reshape((test_inp.shape[0], 1, test_inp.shape[1]))
    #
    # test_ekf = test_data[:, 13:-1]
    # test_ekf = test_ekf.reshape((test_ekf.shape[0], 1, test_ekf.shape[1]))
    #
    # test_out = loadtxt(f"{data_path}/{opti_file[2]}", delimiter=',')  # numpy array
    # test_out = test_out.reshape((test_out.shape[0], 1, test_out.shape[1]))
    #
    #
    #
    #
    # print(training.shape, target.shape, ekf_target.shape)
    # print(val_inp.shape, val_out.shape, val_ekf.shape)
    #
    # inputsize = (1, 12)
    # outputsize = (6, 1)
    #
    # NN = getRNNmodel(inputsize, outputsize)
    #
    # print("before compiling model")
    # NN.compile(loss=loss_possibilities[2], optimizer=optimizer_possibilities[1], metrics=['accuracy'])
    #
    # # The batch size is a number of samples processed before the model is updated
    # # The number of epochs is the number of complete passes through the training dataset
    # print("before training model")
    # print(f"input data shape: {training.shape}, target data shape: {target.shape}")
    # print(f"defined input dim: {inputsize}, data input size: {training[0].shape}")
    # print(f"defined output dim: {outputsize}, data output size: {target[0].shape}")
    # NN.fit(training, target, epochs=25, batch_size=5000, validation_data=(val_inp, val_out))
    #
    # NN.save_weights('test_run')
    # NN.load_weights('test_run')
    #
    # results = NN.evaluate(test_inp, test_out, batch_size=2000)
    # print(f"test loss: {results[0]} and test accuracy: {results[1]}")
    # node = [10, 4]
    # activation = ['relu', 'sigmoid']
    # NN = get_NN_model(indim, node, activation)

    """
    inputsize = 12
    outputsize = 6

    NN = getRNNmodel(inputsize, outputsize)
    loss_possibilities= ['binary_crossentropy', 'sparse_categorical_crossentropy']
    optimizer_possibilities = ['adam', tf.keras.optimizers.Adam(lr=0.001, decay=1e-6)]
    NN.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])


    # evaluate keras model
    _, accuracy = NN.evaluate(training, target)



    # compile the keras model
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    # fit the keras model on the dataset
    model.fit(X, y, epochs=150, batch_size=10)
    # evaluate the keras model
    _, accuracy = model.evaluate(X, y)
    print('Accuracy: %.2f' % (accuracy * 100))
"""


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    now = datetime.now()
    date_time = now.strftime("%Y_%m_%d_%H_%M_%S")
    spath = f"{os.getcwd()}\{date_time}_final_test_sensor__rand_test"
    flag_save_code = True

    if not os.path.isdir(spath):
        os.mkdir(spath)

    if flag_save_code:

        print(spath, dataset_number)
        cpath = "C:/Users/ASUS/PycharmProjects/pythonProject/main.py"
        codef = open(cpath, "r")
        fname = f"{spath}\main.txt"
        # if not os.path.isfile(fname):
        #     os.mkfile

        textf = open(fname, 'w')
        for line in codef:
            textf.write(line)
        textf.close()
        codef.close()

    inputsize = (1, 19)
    # only ekf data to optitrack data
    inputsize = (1, 12)
    outputsize = (6, 1)
    main(inputsize, outputsize, spath)
    evaluate_network(spath)
    # testmain(spath)
    print_hi('PyCharm')