from receive_image import get_and_save_image, serial_conf


def testing(card_name, reps):
    wd = 320    # change requires arduino code modification
    hg = 240    # change requires arduino code modification
    rdy = '*RDY*'   # change requires arduino code modification

    ser = serial_conf('COM2')

    for i in range(reps):
        img_name = f'testy/{card_name}{i}.bmp'
        get_and_save_image(ser, img_name, wd, hg, rdy)
        print(f'Saved image nr {i}')

    ser.close()


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


# test1()
