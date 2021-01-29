


# read single image and plot 16 transformations with matplotlib.pyplot
def plot_16():
    image = plt.imread('images/3 karo.jpg')
    images = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
        #imshow(images[0])
        #show()
    data_generator = ImageDataGenerator(rotation_range=90, brightness_range=(0.5, 1.5), shear_range=15.0, zoom_range=[.3, .8])
    data_generator.fit(images)
    image_iterator = data_generator.flow(images)
    plt.figure(figsize=(16,16))
    for i in range(16):
        plt.subplot(4,4,i+1)
        plt.xticks([])
        plt.yticks([])
        plt.grid(False)
        plt.imshow(image_iterator.next()[0].astype('int'))
        print(i)
    plt.show()
#plot_16()


    # overcomplicated guessing multiple transformations
    """
    prediction = []
    for i in range(10):
        img_transformed = image_iterator.next()[0].astype('int') / color_scale
        prediction.append(model.predict(np.array([img_transformed])))
    data = []
    local_max_probability = 0
    max_probability_list = []
    for element in prediction:
        element_list = element[0].tolist()
        data.append(element_list.index(max(element_list)))
        if max(element_list) > local_max_probability:
            local_max_probability = max(element_list)
        max_probability_list.append(local_max_probability ** 6)
        local_max_probability = 0

    max_element = data[0]
    if len(set(data)) > 1:
        weighted_elements = []
        i = 0
        for candidate in sorted(set(data)):
            weighted_elements.append(0)
            j = 0
            for element in data:
                if candidate == element:
                    weighted_elements[i] += max_probability_list[j]
                j += 1
            i += 1
        max_element = sorted(set(data))[weighted_elements.index(max(weighted_elements))]

    return max_element
"""