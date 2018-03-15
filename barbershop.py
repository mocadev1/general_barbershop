from random import Random
from threading import BoundedSemaphore, Thread

import argparse
import time


# barber
# args: 
# seats_available: The semaphore controlling access to the waiting room
# barber_available: The semaphore controlling access to the barber
# close_barbershop: The semaphore controlling whether the barbershop is open
# min_cut_time: The minimum amount of time it takes for the barber to cut hair
# max_cut_time: The maximum amount of time it takes the barber to cut hair
def barber(seats_available, barber_available, close_barbershop, min_cut_time, max_cut_time):
    while True:
        # print("Barber is awake")
        try:
            seats_available.release()       # release a seat in the waiting room
            barber_available.release()      # signal that the haircut is in progress and the barber is not available (1)
            time.sleep(get_random_interval(min_cut_time, max_cut_time))  # Simulate hair cut
        except ValueError:
            # Sleep (do nothing) or exit if shop is closed
            if close_barbershop.acquire(False):
                break
    print("Barber is asleep")


# customer
# args:
# seats_available: The semaphore controlling access to the waiting room
# barber_available: The semaphore controlling access to the barber
# number: The customer's spot in line
def customer(seats_available, barber_available, number=0):
    print("Customer {} is entering the store.".format(number))
    if seats_available.acquire(False):
        barber_available.acquire()        # signal that the haircut is finished and the barber is available (0)
        print("Customer {} is done getting a haircut.".format(number))   # print finished message
    else:   # else all seats are full
        print("Customer {} could not find an open chair and is leaving.".format(number))
        return


# get_random_interval
# args:
# min_time: The minimum amount of time allowed
# max_time: The maximum amount of time allowed
# return:
# Integer value randomly generated within the range defined by the parameters
def get_random_interval(min_time, max_time):
    rand = Random()         # initialize the Random class
    return rand.randint(    # return a random integer within range
        min_time,
        max_time
    )


# main
# args: The parsed command line inputs
# Spawns new customers while the barbershop is open.
# Closes barbershop when the specified time limit is up.
def main(args):
    # parse from args array into local vars
    seats = args.seats                                          # number of seats in the barbershop
    barber_duration = args.duration                             # number of seconds to run simulation
    min_customer_time, max_customer_time = args.waitrange       # range of seconds to wait between customer arrivals
    min_cut_time, max_cut_time = args.cutrange                  # range of time it takes barber to cut hair

    finish = time.time() + barber_duration                      # set end simulation time

    seats_available = BoundedSemaphore(seats)  # initialize semaphore that indicates if waiting room seats are available
    barber_available = BoundedSemaphore(1)     # initialize semaphore that indicates if the barber is available
    close_barbershop = BoundedSemaphore(1)     # initialize semaphore that indicates if the barbershop is open

    barber_available.acquire()                       # set barber state to available (0)
    close_barbershop.acquire()                       # set barbershop state to open (0)

    threads = [Thread(target=barber,                 # initialize barber thread
                      args=(seats_available,
                            barber_available,
                            close_barbershop,
                            min_cut_time,
                            max_cut_time))]
    threads[0].start()                               # start barber thread

    i = 0                                            # initialize thread counter
    while time.time() < finish:                      # while simulation is running
        threads.append(Thread(target=customer,       # add a customer thread
                              args=(seats_available,
                                    barber_available,
                                    i)))
        threads[len(threads) - 1].start()            # start the next customer thread

        i += 1                                       # increment customer counter
        rand_sleep_time = get_random_interval(       # get a random time to sleep in range
            min_customer_time,
            max_customer_time
        )
        time.sleep(rand_sleep_time)                  # wait for next customer to arrive

    print("Closing barbershop")     # when simulation time is up
    close_barbershop.release()      # set barbershop state to closed (1)
    for thread in threads:          # cleanup child threads
        thread.join()


arguments = 0
if __name__ == "__main__":
    # Set up command line argument parser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description="Run a simulation of the Sleeping Barber's Problem")
    # Interpret -s argument as number of seats in the barbershop
    parser.add_argument('-s', '--seats', type=int, default=3,
                        help="number of seats in barbershop")
    # Interpret -d as ow long the barbershop simulation will run in seconds
    parser.add_argument('-d', '--duration', type=int, default=60,  # default=30,
                        help="how long the barbershop is open (seconds)")
    # Interpret -c as how long a haircut will take in seconds (range)
    parser.add_argument('-c', '--cutrange', type=int, default=[3, 8], nargs=2,  # default=[1, 1], nargs=2,
                        help="range of times for how long a haircut takes (seconds)")
    # Interpret -w as how long it takes for a new customer to arrive (seconds)
    parser.add_argument('-w', '--waitrange', type=int, default=[1, 6], nargs=2,
                        help="range of times for customer arrivals (seconds)")
    # Assign parsed arguments
    arguments = parser.parse_args()

# Begin main
main(arguments)
