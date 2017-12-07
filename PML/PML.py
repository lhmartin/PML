# Python Machine Learning Module
# A project made for the purpose practising Machine Learning Concepts
# Built in reference to techniques shown in Andrew Ng's Deep Learning Course
# Inspired by Andrej Karpathy's JS library
# Project by: Luke Martin

import numpy as np
import matplotlib.pyplot as plt


class Network:
    """

    """
    def __init__(self, layers):
        self.layers = []
        self.L = 0

        for layer in layers:
            self.add_layer(layer)

    def add_layer(self, layer):
        self.layers.append(layer)
        self.L += 1

    def forward_propagate(self, input_data):
        A = input_data
        L = self.L
        for l in range(L):
            A = self.layers[l].forward_propagate(A)

        return A

    def back_propagate(self, labels, AL):
        L = self.L
        # dA = -1 * (np.divide(labels, AL) - np.divide(1 - labels, 1 - AL))

        for l in reversed(range(L)):
            if l is L - 1:
                dZ = AL - labels
                # dZ = -(np.divide(labels, AL) - np.divide(1 - labels, 1 - AL))
                self.layers[l].dZ = dZ
            else:
                dZ = self.layers[l].back_propagate(self.layers[l+1].dZ, self.layers[l+1].W)

            self.layers[l].linear_backward(dZ)

        # for l in reversed(range(L)):
         # self.layers[l].back_propagate(dA)
            # dZ = self.layers[l].sigmoid_backward(dA) # Requires dA
            # _,_, dA = self.layers[l].linear_backward(dZ)  # Require dZ

    def predict(self, input_data):
        AL = self.forward_propagate(input_data)
        if(self.layers[self.L - 1].act_func is "sigmoid"):
            prediction = 1*(AL > 0.5)
        elif(self.layers[self.L - 1].act_func is "softmax"):
            prediction = AL
            # TODO: fix the softmax predictor

        # TODO: Change this based on the type of output layer. (softmax, Logistic)
        return prediction


    def plot_decision_boundary(self, X, y):
        # Set min and max values and give it some padding
        x_min, x_max = X[:, 0].min() - .5, X[:, 0].max() + .5
        y_min, y_max = X[:, 1].min() - .5, X[:, 1].max() + .5

        h = 0.01
        # Generate a grid of points with distance h between them
        xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

        mesh_points = np.array([xx.ravel(), yy.ravel()])

        # Predict the function value for the whole gid
        Z = self.predict(mesh_points)
        Z = Z.reshape(xx.shape)
        # Plot the contour and training examples
        plt.contourf(xx, yy, Z, cmap=plt.cm.Spectral)
        plt.scatter(X[:, 0], X[:, 1], c=y, cmap=plt.cm.Spectral)
        plt.show()

class Optimizer:
    """

    """
    def __init__(self, net, learning_rate=0.1):
        self.network = net
        self.learning_rate = learning_rate
        self.costs = []

    def train(self, input_data, labels, iterations=10000):
        for i in range(iterations):

            AL = self.network.forward_propagate(input_data)
            cost = self.compute_cost(labels, AL)
            self.network.back_propagate(labels, AL)
            self.update_parameters()
            if i % 1000 is 0:
                print("iteration: ",i," cost = ", cost)
                self.costs.append(cost)

    def compute_cost(self, Y, AL):
        """

        :param Y:
        :param AL:
        :return:
        """
        # TODO: Update this to be more versatile
        m = Y.shape[1]
        logprobs = np.multiply(np.log(AL), Y) + np.multiply(np.log(1 - AL), 1 - Y)
        cost = -1 *np.sum(logprobs) * (1 / m)
        cost = np.squeeze(cost)
        assert (cost.shape == ())
        return cost

    def update_parameters(self):
        L = len(self.network.layers)
        for l in range(L):
            self.network.layers[l].W = self.network.layers[l].W - self.network.layers[l].dW * self.learning_rate
            self.network.layers[l].b = self.network.layers[l].b - self.network.layers[l].db * self.learning_rate

    def plot_cost(self):
        plt.plot(np.array(self.costs))
        # plt.axis(0, 5, 0, 10000)
        plt.show()

    def compute_accuracy(self, X, labels):
        accuracy = 0.0

        AL = self.network.predict(X)

        predictions = AL.argmax(axis=0)

        print("Predictions = ", predictions)
        print("True labels = ", labels)
        print("Correct = ", predictions == labels)

        accuracy = sum(1*(predictions == labels)) / labels.shape[0]

        return accuracy

class Layer:
    def __init__(self, act_func, type="fc"):
        self.n_x = None
        self.n_h = None

        self.act_func = act_func

        self.layer_type = None

        self.W = None
        self.b = None

        self.A = None
        self.Z = None
        self.A_prev = None

        self.dZ = None
        self.dW = None
        self.db = None
        self.dA = None

        self.type = type

        if type is "conv":
            self.stride = None
            self.pad = None

    def initialize(self, n_x, n_h, pad=None, stride=None):
        """
        :param n_x: size of input layer
        :param n_h: size of hidden layer
        :param layer_type: the type of the layer
        """
        self.n_x = n_x
        self.n_h = n_h

        self.W = np.random.randn(n_h, n_x) * 0.1
        self.b = np.zeros((n_h, 1))

        assert (self.W.shape == (n_h, n_x))
        assert (self.b.shape == (n_h, 1))

        return self.W, self.b

    def zero_pad(X, pad):

        X_pad = np.pad(X, ((0, 0), (pad, pad), (pad, pad), (0, 0)), "constant")

        return X_pad

    def linear_forward(self, input_A):
        self.A_prev = input_A
        self.Z = np.dot(self.W, input_A) + self.b

        return self.Z

    def relu_forward(self, Z):
        self.A = np.maximum(Z, 0)
        return self.A

    def relu_backward(self, dZ_prev, W_prev):
        dA = np.dot(W_prev.T, dZ_prev)
        self.dZ = 1*(dA > 1)
        return self.dZ

    def tanh_forward(self, Z):
        self.A = np.tanh(Z)
        return self.A

    def tanh_backward(self, dZ_prev, W_prev):
        dA = np.dot(W_prev.T, dZ_prev)
        self.dZ = dA * (1 - np.power(self.A, 2))
        return self.dZ

    def sigmoid_forward(self, Z):
        self.A = 1/(1 + np.exp(-Z))
        return self.A

    def sigmoid_backward(self, dZ_prev, W_prev):

        dA = np.dot(W_prev.T, dZ_prev)
        sig_deriv = np.exp(self.Z) / np.power((np.exp(self.Z) + 1), 2)
        self.dZ = dA * sig_deriv
        return self.dZ

    def softmax_forward(self, Z):
        Z_e = np.exp(Z)
        self.A = Z_e / np.sum(Z_e, axis=0)
        return self.A

    def softmax_backward(self):
        return None

    def linear_backward(self, dZ):
        """

        :param dZ:
        :return: The gradients of the layer
        """
        # Need W_prev, dZ_prev
        # dZ = A - Y for output layer
        # dZ = np.dot(W2.T, dZ2) * (1 - np.power(A1, 2))
        m = self.A_prev.shape[1]

        self.dW = (1 / m) * np.dot(dZ, self.A_prev.T)
        self.db = (1 / m) * np.sum(dZ, axis=1, keepdims=True)

        return self.dW, self.db

    def conv_single_step(self, a_slice, W, b):
        Z = np.sum(a_slice*W) + float(b)
        return Z

    def conv_forward(self, A_prev):
        ## GRADED FUNCTION: conv_forward
        (m, n_H_prev, n_W_prev, n_C_prev) = A_prev.shape

        (f, f, n_C_prev, n_C) = self.W.shape

        stride = self.stride
        pad = self.pad

        n_H = int((n_H_prev - f + 2 * pad) / stride) + 1
        n_W = int((n_W_prev - f + 2 * pad) / stride) + 1

        # Initialize the output volume Z with zeros. (≈1 line)
        self.Z = np.zeros((m, n_H, n_W, n_C))

        # Create A_prev_pad by padding A_prev
        A_prev_pad = self.zero_pad(A_prev, pad)

        for i in range(m):  # loop over the batch of training examples
            a_prev_pad = A_prev_pad[i, :, :, :]  # Select ith training example's padded activation
            for h in range(n_H):  # loop over vertical axis of the output volume
                for w in range(n_W):  # loop over horizontal axis of the output volume
                    for c in range(n_C):  # loop over channels (= #filters) of the output volume

                        # Find the corners of the current "slice"
                        vert_start = h * stride
                        vert_end = h * stride + f
                        horiz_start = w * stride
                        horiz_end = w * stride + f

                        # Use the corners to define the (3D) slice of a_prev_pad (See Hint above the cell)
                        a_slice_prev = a_prev_pad[vert_start:vert_end, horiz_start:horiz_end, :]

                        # Convolve the (3D) slice with the correct filter W and bias b, to get back one output neuron.
                        self.Z[i, h, w, c] = self.conv_single_step(a_slice_prev, self.W[:, :, :, c], self.b[:, :, :, c])

            assert (self.Z.shape == (m, n_H, n_W, n_C))
        return self.Z


    def back_propagate(self, dZ_prev, W_prev):
        dZ = None
        if self.act_func is "sigmoid":
            dZ = self.sigmoid_backward(dZ_prev, W_prev)
        elif self.act_func is "relu":
            dZ = self.relu_backward(dZ_prev, W_prev)
        elif self.act_func is "tanh":
            dZ = self.tanh_backward(dZ_prev, W_prev)
        return dZ

    def forward_propagate(self, prev_A):
        Z = self.linear_forward(prev_A)
        A = None
        if self.act_func is "tanh":
            A = self.tanh_forward(Z)
        elif self.act_func is "sigmoid":
            A = self.sigmoid_forward(Z)
        elif self.act_func is "relu":
            A = self.relu_forward(Z)
        elif self.act_func is  "softmax":
            A = self.softmax_forward(Z)

        return A