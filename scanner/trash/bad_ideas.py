


#from PIL import Image
def get_threshold(image_arr):
    image_list = []
    for row in image_arr:
        for element in row:
            image_list.append(element[0])
    # for element in set(image_list):
        # print(element, image_list.count(element))
    threshold = sum(image_list)
    threshold = threshold/(image_arr.shape[0]*image_arr.shape[1])
    return threshold, statistics.median(image_list)

def simplier(image_arr, threshold):
    for row in image_arr:
        for element in row:
            if element[0] < threshold + 10:
                element[0] = 0
    return image_arr


def process_image_A(path_to_file):
    image = Image.open(path_to_file).convert('LA')
    print(image)
    MAX_SIDE = 200
    rescale_value = 1
    while rescale_value * MAX_SIDE < max(image.size):
        rescale_value += 1
    image = image.resize((round(image.size[0] / rescale_value), round(image.size[1] / rescale_value)))
    image_arr = np.array(image)



    new_image = simplier(image_arr, get_threshold(image_arr)[0])
    Image.fromarray(new_image, 'LA').show()
    # print(image_arr.shape)
    # print(image.format)
    # print(image.size)
    # print(image.mode)


process_image_A('images/3 karo.jpg')


"""
#simple 1-layer feed-forward neural
class NeuralNetwork():

    def __init__(self):
        # seeding for random number generation
        np.random.seed(1)

        # converting weights to a 3 by 1 matrix with values from -1 to 1 and mean of 0
        self.synaptic_weights = 2 * np.random.random((3, 1)) - 1

    def sigmoid(self, x):
        # applying the sigmoid function
        return 1 / (1 + np.exp(-x))

    def sigmoid_derivative(self, x):
        # computing derivative to the Sigmoid function
        return x * (1 - x)

    def train(self, training_inputs, training_outputs, training_iterations):
        # training the model to make accurate predictions while adjusting weights continually
        for iteration in range(training_iterations):
            # siphon the training data via  the neuron
            output = self.predict(training_inputs)

            # computing error rate for back-propagation
            error = training_outputs - output

            # performing weight adjustments
            adjustments = np.dot(training_inputs.T, error * self.sigmoid_derivative(output))

            self.synaptic_weights += adjustments

    def predict(self, inputs):
        # passing the inputs via the neuron to get output
        # converting values to floats

        inputs = inputs.astype(float)
        output = self.sigmoid(np.dot(inputs, self.synaptic_weights))
        return output



neural_network = NeuralNetwork()

print("Weights before training: ")
print(neural_network.synaptic_weights)
print("Predicting [0, 0, 1]: ", neural_network.predict(np.array([0, 0, 1])))

# training data
training_inputs = np.array([[0, 0, 1], [1, 1, 1], [1, 0, 1], [0, 1, 1]])
training_outputs = np.array([[0, 1, 1, 0]]).T   #.T transponuje macierz

neural_network.train(training_inputs, training_outputs, 100000)

print("Weights After Training: ")
print(neural_network.synaptic_weights)

print("Predicting [0, 0, 1]: ",neural_network.predict(np.array([0, 0, 0])))
print("Predicting [1, 1, 1]: ", neural_network.predict(np.array([0, 0, 1])))
"""