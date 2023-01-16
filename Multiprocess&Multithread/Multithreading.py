import logging
import threading
import time


def thread_lucky_function(name, count_from, count_to, counter=0):
    logging.info(f"Thread {name}: starting")
    start_time = time.time()
    for itm in range(count_from, count_to):
        itm = f"{itm:06}"
        if lucky_ticket(str(itm)):
            counter += 1

    print(f"Thread {name} work time is {time.time() - start_time}")
    logging.info(f"Thread {name}: finishing with {counter} lucky tickets")


def lucky_ticket(ticket_number):
    if len(ticket_number) == 6:
        if sum(int(i) for i in ticket_number[:3]) == sum(int(i) for i in ticket_number[3:]):
            return True
        else:
            return False


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    logging.info("Main    : before creating threads")
    x = threading.Thread(target=thread_lucky_function, args=('First', 1, 999999,))
    y = threading.Thread(target=thread_lucky_function, args=('Second', 1, 999999,))
    logging.info("Main    : before starting threads")
    x.start()
    logging.info("Main    : First thread is started")
    y.start()
    logging.info("Main    : Second thread is started")
