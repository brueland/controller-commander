# File: input_reader.py
import math
from inputs import get_gamepad


def apply_deadzone(value, deadzone):
    if abs(value) < deadzone:
        return 0
    return (value - math.copysign(deadzone, value)) / (1 - deadzone)


class InputReader:
    def __init__(self, deadzone=0.1):
        self.deadzone = deadzone
        self.x_axis = 0
        self.y_axis = 0
        self.right_y_axis = 0
        self.buttons = {}

    def read_input(self):
        events = get_gamepad()
        for event in events:
            if event.ev_type == "Absolute":
                if event.code == "ABS_X":
                    self.x_axis = apply_deadzone(event.state / 32768, self.deadzone)
                elif event.code == "ABS_Y":
                    self.y_axis = apply_deadzone(event.state / 32768, self.deadzone)
                elif event.code == "ABS_RY":
                    self.right_y_axis = apply_deadzone(
                        event.state / 32768, self.deadzone
                    )
                elif event.code in ["ABS_HAT0X", "ABS_HAT0Y"]:
                    self.buttons[event.code] = event.state
            elif event.ev_type == "Key":
                self.buttons[event.code] = event.state
        return self.x_axis, self.y_axis, self.right_y_axis, self.buttons
