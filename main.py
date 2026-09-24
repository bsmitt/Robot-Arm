import pygame

import sys

import serial

import time



try:

    ser = serial.Serial('COM3', 115200, timeout=1)

    time.sleep(2)  # Allow time for serial connection to establish

    print("Serial connected to Pico!")

except Exception as e:

    print(f"Serial connection failed: {e}")

    ser = None



pygame.init()

pygame.font.init()



screen = pygame.display.set_mode((1300, 500))

pygame.display.set_caption("Xbox Controller On-Screen Display")



pygame.joystick.init()



try:

    font = pygame.font.SysFont("Arial", 22)

except Exception:

    font = pygame.font.Font(None, 26)



joystick_count = pygame.joystick.get_count()

controller_name = "No controller found"



if joystick_count > 0:

    controller = pygame.joystick.Joystick(0)

    controller.init()

    controller_name = controller.get_name()



# 1. Define custom name mappings for Xbox controllers

BUTTON_NAMES = {

    0: "A",

    1: "B",

    2: "X",

    3: "Y",

    4: "LB",

    5: "RB",

    6: "Back",

    7: "Start",

    8: "L3",

    9: "R3",

    10: "Xbox Guide",

    11: "Share"

}



AXIS_NAMES = {

    0: "Left Stick X",

    1: "Left Stick Y",

    2: "Right Stick X",

    3: "Right Stick Y",

    4: "LT",

    5: "RT"

}



button_states = {}

axis_states = {}

hat_value = (0, 0)



clock = pygame.time.Clock()

running = True



while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False



        elif event.type == pygame.JOYBUTTONDOWN:

            # Map the integer index to a human-readable name

            button_name = BUTTON_NAMES.get(event.button, f"Button {event.button}")

            button_states[button_name] = "pressed"



        elif event.type == pygame.JOYBUTTONUP:

            button_name = BUTTON_NAMES.get(event.button, f"Button {event.button}")

            button_states[button_name] = ""



        elif event.type == pygame.JOYAXISMOTION:

            # Map the integer axis index to a human-readable name

            axis_name = AXIS_NAMES.get(event.axis, f"Axis {event.axis}")

            if abs(event.value) > 0.1:

                axis_states[axis_name] = round(event.value, 2)

            else:

                axis_states[axis_name] = 0.0



        elif event.type == pygame.JOYHATMOTION:

            hat_value = event.value



    screen.fill((30, 30, 30))



    texts = [

        f"Controller: {controller_name}",

        f"Last Hat (D-Pad): {hat_value}",

        f"Buttons: {button_states}",

        f"Axes: {axis_states}"

    ]



    y_offset = 30

    for text_line in texts:

        surface = font.render(text_line, True, (240, 240, 240))

        screen.blit(surface, (30, y_offset))

        y_offset += 40



    pygame.display.flip()

    clock.tick(60)



pygame.quit()

sys.exit()