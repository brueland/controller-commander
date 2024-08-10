# File: main.py
import multiprocessing
import threading
import pystray
from PIL import Image, ImageDraw
from controller_mapper import ControllerMapper


def create_image():
    image = Image.new("RGB", (64, 64), color=(73, 109, 137))
    d = ImageDraw.Draw(image)
    d.text((10, 10), "CM", fill=(255, 255, 0))
    return image


def check_exit_queue(exit_queue, stop_event, icon):
    while not stop_event.is_set():
        try:
            message = exit_queue.get(timeout=0.1)
            if message == "exit":
                stop_event.set()
                icon.stop()
                break
        except multiprocessing.queues.Empty:
            continue


def run_mapper(stop_event, exit_queue):
    mapper = ControllerMapper(stop_event, exit_queue)
    mapper.run()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    stop_event = multiprocessing.Event()
    exit_queue = multiprocessing.Queue()

    mapper_process = multiprocessing.Process(
        target=run_mapper, args=(stop_event, exit_queue)
    )
    mapper_process.start()

    def exit_action(icon):
        stop_event.set()
        exit_queue.put("exit")
        icon.stop()
        mapper_process.join(timeout=5)
        if mapper_process.is_alive():
            print("Forcing mapper process to terminate...")
            mapper_process.terminate()
        print("Exiting...")

    image = create_image()
    menu = pystray.Menu(pystray.MenuItem("Exit", exit_action))
    icon = pystray.Icon("controller_mapper", image, "Controller Mapper", menu)

    exit_check_thread = threading.Thread(
        target=check_exit_queue, args=(exit_queue, stop_event, icon)
    )
    exit_check_thread.daemon = True
    exit_check_thread.start()

    icon.run()

    stop_event.set()
    exit_queue.put("exit")
    mapper_process.join(timeout=5)
    if mapper_process.is_alive():
        print("Forcing mapper process to terminate...")
        mapper_process.terminate()
    exit_check_thread.join(timeout=5)
    print("Script exited successfully")
