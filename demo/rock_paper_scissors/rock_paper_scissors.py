import glob
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from spektral.layers import GraphConv, GlobalMaxPool
from spektral.utils import conversion
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import Input, Dense, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from utils.networkx_converter import get_nx_graphs
import json


def __get_graph_list(shape):
    """
    Given a shape, returns a list of networkx graphs representing hands
    with the given shape
    :param str shape: string representing a shape. One of: 'paper',
    'scissor' or 'rock'
    :return list: list of networkx graphs
    """
    graph_list = []
    files = glob.glob('../../' + shape + '/*.json')
    for file in files:
        with open(file) as json_file:
            data = json.load(json_file)
        graph_list.extend(
            get_nx_graphs(data,
                          dict(pose=False, hand=True, face=False),
                          normalize=True)
        )
    return graph_list


def __add_onehot(matrix_list):
    """
    Given a list of matrices, append on each matrix in the list an
    identity matrix
    :param matrix_list: numpy array of matrices
    :return: numpy array of matrices
    """
    label_list = np.repeat([np.identity(21)], matrix_list.shape[0], axis=0)
    matrix_list = np.concatenate([matrix_list, label_list], axis=-1)
    return matrix_list


def __standardize_data(adj_lst, pred_lst, y_lst):
    """
    Given a list of adj matrices, a list of matrices representing the
    predictor values for each graph, and a list of outputs, remove the
    graphs with mean precision is greater than 50%, subtracts the mean
    and divide with the std
    :param numpy array adj_lst: numpy array of adj matrices
    :param numpy array pred_lst: numpy array of matrix-predictors
    :param numpy array y_lst: list of outputs
    :return 3x numpy arrays: A_norm, X_norm and y_norm normalized
    """

    fil = np.full(y_lst.shape[0], fill_value=True)
    for i in range(y_lst.shape[0]):
        fil[i] = (pred_lst[i, :, 2] > .7).mean() > .5
    adj_lst_std, pred_lst_std, y_std = adj_lst[fil], pred_lst[fil], y_lst[fil]

    pred_lst_std = __add_onehot(pred_lst[:, :, :2])
    pred_lst_std -= pred_lst_std.mean(axis=1, keepdims=True)
    pred_lst_std /= pred_lst_std.std(axis=1, keepdims=True)
    return adj_lst, pred_lst_std, y_lst


def __generate_data():
    print('Generating networkx graphs...', end='')
    paper_graphs = __get_graph_list('paper')
    rock_graphs = __get_graph_list('rock')
    scissors_graphs = __get_graph_list('scissors')
    print('done')
    print('Converting to numpy matrix...', end='')
    paper_matrix = conversion.nx_to_numpy(
        paper_graphs, nf_keys=['x', 'y', 'confidence']
    )
    rock_matrix = conversion.nx_to_numpy(
        rock_graphs, nf_keys=['x', 'y', 'confidence']
    )
    scissors_matrix = conversion.nx_to_numpy(
        scissors_graphs, nf_keys=['x', 'y', 'confidence']
    )
    A = np.append(paper_matrix[0],
                  np.append(rock_matrix[0],
                            scissors_matrix[0],
                            axis=0),
                  axis=0)
    X = np.append(paper_matrix[1],
                  np.append(rock_matrix[1],
                            scissors_matrix[1],
                            axis=0),
                  axis=0)
    y = np.append(
        np.repeat([[1.0, 0.0, 0.0]], paper_matrix[0].shape[0], axis=0),
        np.append(
            np.repeat([[0.0, 1.0, 0.0]], rock_matrix[0].shape[0], axis=0),
            np.repeat([[0.0, 0.0, 1.0]], scissors_matrix[0].shape[0], axis=0),
            axis=0
        ), axis=0)
    print('done')
    return __standardize_data(A, X, y)


def __plot_results(fit_res):
    """
    Plots accuracy and loss for both train and test datasets.
    :param fit_res: dictionary generated by keras.fit
    """
    # Plot training & validation accuracy values
    plt.subplot(2, 1, 1)
    plt.plot(fit_res.history['acc'])
    plt.plot(fit_res.history['val_acc'])
    plt.title('Model accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Test'], loc='upper left')

    # Plot training & validation loss values
    plt.subplot(2, 1, 2)
    plt.plot(fit_res.history['loss'])
    plt.plot(fit_res.history['val_loss'])
    plt.title('Model loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Test'], loc='upper left')
    plt.subplots_adjust(hspace=0.5)
    plt.show()


if __name__ == "__main__":
    A, X, y = __generate_data()

    # Parameters
    n_nodes = X.shape[-2]
    n_variables = X.shape[-1]
    n_classes = y.shape[-1]
    learning_rate = 1e-4
    epochs = 20000
    batch_size = 64
    es_patience = 200
    lr_patience = 5

    # Create train and test datasets
    A_train, A_test, x_train, x_test, y_train, y_test = \
        train_test_split(A, X, y, test_size=0.2)

    # Create model
    X_in = Input(shape=(n_nodes, n_variables))
    A_in = Input((n_nodes, n_nodes))
    gc = Dropout(0.2)(X_in)
    gc = GraphConv(64, activation='relu')([X_in, A_in])
    gc = Dropout(0.2)(gc)
    gc = GraphConv(64, activation='relu')([gc, A_in])
    gc = Dropout(0.2)(gc)
    gc = GraphConv(64, activation='relu')([gc, A_in])
    gc = Dropout(0.2)(gc)
    pool = GlobalMaxPool()(gc)
    output = Dense(n_classes, activation='softmax')(pool)
    model = Model(inputs=[X_in, A_in], outputs=output)
    optimizer = Adam(lr=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss='categorical_crossentropy',
        metrics=['acc']
    )

    # Train model
    early_stopping = EarlyStopping(
        patience=es_patience,
        restore_best_weights=True
    )
    print('Training the model...', end='')
    history = model.fit(
        [x_train, A_train], y_train,
        batch_size=batch_size,
        validation_split=0.2,
        epochs=epochs,
        callbacks=[early_stopping], verbose=0
    )
    print('done')

    #  Evaluate model
    print('Evaluating model...', end='')
    eval_results = model.evaluate(
        [x_test, A_test],
        y_test,
        batch_size=batch_size,
        verbose=0
    )
    print('done')
    print('Test loss: {:.4f}. Test acc: {:.1f}%'
          .format(eval_results[0], eval_results[1] * 100))

    __plot_results(history)
