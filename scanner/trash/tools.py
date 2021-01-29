import time

class Clock():
    def __init__(self):
        #self.__clock_start = time.time()
        self.__i = 0

    def tick(self, message = None):
        if self.__i % 2 == 0:
            self.__clock_start = time.time()
        else:
            print(time.time() - self.__clock_start)
            if message is not None:
                print(message)
        self.__i += 1

# most occuring element in list
most_occuring = max(set(data), key = data.count)