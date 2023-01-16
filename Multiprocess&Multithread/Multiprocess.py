import logging
import multiprocessing
import time


def process_lucky_function(name, count_from, count_to, counter=0):
    logging.info(f"Process {name}: starting")
    start_time = time.time()
    for itm in range(count_from, count_to):
        # itm = str(itm).rjust(6, '0')
        itm = f"{itm:06}"
        if lucky_ticket(itm):
            counter += 1

    print(f"Process {name} work time is {time.time() - start_time}")
    print(f"Process {name}: finishing with {counter} lucky tickets")


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

    logging.info("Main    : before creating processes")
    x = multiprocessing.Process(target=process_lucky_function, args=('First', 1, 999999,))
    y = multiprocessing.Process(target=process_lucky_function, args=('Second', 1, 999999,))
    logging.info("Main    : before starting processes")
    x.start()
    logging.info("Main    : First process is started")
    y.start()
    logging.info("Main    : Second process is started")
    time.sleep(3)
    logging.info("Main    : all process are done")


