import logging
import multiprocessing
import time

counter_list = []
process_tuple = ('First', 'Second', 'Third', 'Fourth',)
sum_list = []
qe = multiprocessing.Queue()


def process_lucky_function(name, count_from, count_to, queue, counter=0):
    logging.info(f"Process {name}: starting")
    start_time = time.time()
    for itm in range(count_from, count_to):
        itm = f"{itm:06}"
        if lucky_ticket(str(itm)):
            counter += 1

    queue.put(counter)
    print(f"Process {name} work time is {time.time() - start_time}")
    print(f"Process {name}: finishing with {counter} lucky tickets")
    print(f"Counter value: {counter}")
    print()


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
    logging.info("Main    : before starting any processes")

    for names in process_tuple:
        if names == "First":
            range_from = 1
            range_to = 250000
        elif names == "Second":
            range_from = 250001
            range_to = 500000
        elif names == "Third":
            range_from = 500001
            range_to = 750000
        elif names == "Fourth":
            range_from = 750001
            range_to = 999999
        else:
            range_from = 000000
            range_to = 999999
        proc = multiprocessing.Process(target=process_lucky_function, args=(names, range_from, range_to, qe,))
        counter_list.append(proc)
        proc.start()
        logging.info(f"Main    : {names} process is started")

    for proc in counter_list:
        n = qe.get()
        sum_list.append(n)
        proc.join()

    print(f"General amount of lucky tickets is {sum(sum_list)}")

