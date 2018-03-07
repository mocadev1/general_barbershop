from random import Random
from threading import BoundedSemaphore, Thread

import argparse
import time


def barber(seats_available, cut_done, close_barber, min_cut_time, max_cut_time):
    while True:
        try:
            seats_available.release()
            print("Cutting hair")
            # Simulate hair cut
            time.sleep(get_random_interval(min_cut_time, max_cut_time))
            cut_done.release()
        except ValueError:
            # Sleep (do nothing) or exit if shop is closed
            if close_barber.acquire(False):
                break
    print("Barber closed!")


def customer(seats_available, cut_done, number=0):
    print("Customer {} entering store".format(number))
    if seats_available.acquire(False):
        cut_done.acquire()
        print("Customer {} done getting haircut".format(number))
    else:
        print("Customer {} could not find an open chair".format(number))
        return


def get_random_interval(min_time, max_time):
    rand = Random()
    return rand.randint(min_time, max_time)


def main(args):
    seats = args.seats
    barber_duration = args.duration  # seconds
    min_customer_time, max_customer_time = args.waitrange
    min_cut_time, max_cut_time = args.cutrange
    seats_available = BoundedSemaphore(seats)
    cut_done = BoundedSemaphore(1)
    close_barber = BoundedSemaphore(1)

    # Set cut_done to 0
    cut_done.acquire()
    # Set close_barber to 0
    close_barber.acquire()
    threads = [Thread(target=barber,
                      args=(seats_available, cut_done, close_barber, min_cut_time, max_cut_time))]
    threads[0].start()
    i = 0
    finish = time.time() + barber_duration
    while time.time() < finish:
        threads.append(Thread(target=customer,
                              args=(seats_available, cut_done, i)))
        threads[len(threads) - 1].start()
        i += 1
        time.sleep(get_random_interval(min_customer_time, max_customer_time))
    print("Closing barbershop")
    close_barber.release()
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description="Run a simulation of the sleeping barber's problem")
    parser.add_argument('-s', '--seats', type=int, default=3, help="number of seats in barbershop")
    parser.add_argument('-d', '--duration', type=int, default=60, help="how long the barbershop is open (seconds)")
    parser.add_argument('-c', '--cutrange', type=int, default=[3, 8], nargs=2, help="range of times for haircuts")
    parser.add_argument('-w', '--waitrange', type=int, default=[1, 6], nargs=2,
                        help="range of times for customer arrivals")
    arguments = parser.parse_args()
main(arguments)