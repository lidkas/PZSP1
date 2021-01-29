from device_connection import ArduinoConnection


def testing(card_name, reps):

    ard_conn = ArduinoConnection()

    for i in range(reps):
        img_name = f'testy/{card_name}{i}.bmp'
        ard_conn.get_and_save_image(img_name)
        print(f'Saved image nr {i}')

    ard_conn.ser.close()


def test1():
    addits = 'abcdefghijklm'
    for addit1 in addits:
        for addit2 in addits:
            print(addit1+addit2)
            testing(f'9C{addit1+addit2}', 10)


def test2():
    testing('JH', 2000)


def test3():
    testing('AS', 2000)


def test4():
    testing('Brak', 20)


test4()
