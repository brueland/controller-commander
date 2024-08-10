# File: controller_mapper.py
import time
import math
import multiprocessing
from keybindings import *
from input_reader import InputReader


class ControllerMapper:
    def __init__(self, stop_event, exit_queue):
        self.stop_event = stop_event
        self.exit_queue = exit_queue
        self.input_reader = InputReader()
        self.max_speed = 15
        self.acceleration = 1.5
        self.scroll_speed = 60
        self.y_held = False
        self.right_held = False
        self.left_held = False

    def run(self):
        ctypes.windll.kernel32.SetConsoleCtrlHandler(None, True)
        while not self.stop_event.is_set():
            current_time = time.perf_counter()
            x_axis, y_axis, right_y_axis, buttons = self.input_reader.read_input()

            self.handle_movement(x_axis, y_axis)
            self.handle_scrolling(right_y_axis)
            self.handle_buttons(buttons)

            if "BTN_START" in buttons and buttons["BTN_START"] == 1:
                self.exit_queue.put("exit")
                return

            # Adaptive sleep
            if abs(x_axis) + abs(y_axis) > 0:
                time.sleep(max(1 / 1000 - (time.perf_counter() - current_time), 0))
            else:
                time.sleep(max(1 / 240 - (time.perf_counter() - current_time), 0))

    def handle_movement(self, x_axis, y_axis):
        move_x = int(
            math.copysign(abs(x_axis) ** self.acceleration * self.max_speed, x_axis)
        )
        move_y = int(
            -math.copysign(abs(y_axis) ** self.acceleration * self.max_speed, y_axis)
        )
        if move_x != 0 or move_y != 0:
            mouse_move(move_x, move_y)

    def handle_scrolling(self, right_y_axis):
        if abs(right_y_axis) > self.input_reader.deadzone:
            scroll_amount = int(right_y_axis * self.scroll_speed)
            mouse_scroll(scroll_amount)

    def handle_buttons(self, buttons):
        if "ABS_HAT0Y" in buttons:
            if buttons["ABS_HAT0Y"] == -1:
                press_key(VK_UP)
            elif buttons["ABS_HAT0Y"] == 1:
                press_key(VK_DOWN)
            else:
                release_key(VK_UP)
                release_key(VK_DOWN)

        if "ABS_HAT0X" in buttons:
            self.handle_dpad_x(buttons["ABS_HAT0X"])

        if "BTN_NORTH" in buttons:
            self.handle_y_button(buttons["BTN_NORTH"])

        if "BTN_EAST" in buttons:
            if buttons["BTN_EAST"]:
                press_key(VK_SPACE)
            else:
                release_key(VK_SPACE)

        if "BTN_SOUTH" in buttons:
            if buttons["BTN_SOUTH"] == 1:
                mouse_left_click(True)
            elif buttons["BTN_SOUTH"] == 0:
                mouse_left_click(False)

        if "BTN_TL" in buttons:
            if buttons["BTN_TL"] == 1:
                mouse_right_click(True)
            elif buttons["BTN_TL"] == 0:
                mouse_right_click(False)

        if "BTN_WEST" in buttons:
            if buttons["BTN_WEST"]:
                press_key(VK_BACK)
            else:
                release_key(VK_BACK)

    def handle_dpad_x(self, state):
        if state == -1:  # Left
            self.left_held = True
            if self.y_held:
                press_key(VK_SHIFT)
                press_key(VK_LEFT)
            else:
                press_key(VK_LEFT)
        elif state == 1:  # Right
            self.right_held = True
            if self.y_held:
                press_key(VK_SHIFT)
                press_key(VK_RIGHT)
            else:
                press_key(VK_RIGHT)
        else:  # Released
            if self.left_held:
                release_key(VK_LEFT)
            if self.right_held:
                release_key(VK_RIGHT)
            self.left_held = False
            self.right_held = False
            if not self.y_held:
                release_key(VK_SHIFT)

    def handle_y_button(self, state):
        self.y_held = state == 1
        if self.y_held:
            press_key(VK_SHIFT)
            if self.left_held:
                press_key(VK_LEFT)
            elif self.right_held:
                press_key(VK_RIGHT)
        else:
            release_key(VK_SHIFT)
            if not self.left_held and not self.right_held:
                release_key(VK_LEFT)
                release_key(VK_RIGHT)
