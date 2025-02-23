import time, os
from struct import unpack

from machine import Pin, PWM
from touch import Device


MAX_SCALE = 100
THRESHOLD = MAX_SCALE // 2
TOUCH_THRESHOLD = 3 * MAX_SCALE // 4
CALIBRATING_TIME = 5000

# self test
FREQ = 500
ALPHA = 0.8

touch_array = Device((28, 27, 26))
led_array = [PWM(Pin(20), FREQ), PWM(Pin(19), FREQ), PWM(Pin(21), FREQ)]


def random_value():
    hw_random = os.urandom(4)
    rng_value = (unpack('I', hw_random)[0])%65535
    for l in led_array:
        l.duty_u16(rng_value)

def main():

    with touch_array as touch:

        all_active = [False]*len(touch.channels)
        last_values = [0.0]*len(touch.channels)

        for l in led_array:
            l.duty_u16(0)

        while True:
            if not (False in all_active):
                random_value()

            touch.update()

            index = 0
            for read_value, led, last_value in zip(touch.channels, led_array, last_values):

                curr_value = int(read_value.level*MAX_SCALE*ALPHA + last_value*(1-ALPHA))

                last_values[index] = curr_value

                if curr_value > TOUCH_THRESHOLD:
                    led.duty_u16(curr_value * 655)
                    all_active[index] ^= True

                elif THRESHOLD < curr_value < TOUCH_THRESHOLD:
                    led.duty_u16(curr_value * 65)
                else:
                    led.duty_u16(0)
                index += 1

            time.sleep(0.01)

if __name__ == '__main__':
    main()

# while True:
#     print('\r', end='')
#     for c,l in zip(cs,ls):
#         print(f'{c.value}    ', end='')
