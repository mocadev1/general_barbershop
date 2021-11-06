from random import Random
from threading import BoundedSemaphore, Event, Thread

import os
import argparse
import time
import datetime

# Third party modules
import keyboard # To finish the program pressing Esc key

# Globals
barbershop = BoundedSemaphore(1)         # semaphore that indicates if the barbershop is available
barber_resource = BoundedSemaphore(1)    # semaphore that indicates if the barber is available
mutex = BoundedSemaphore(1)              # semaphore that allows exclusive access to the waiting_customers variable

barber_sleeping_event = Event()          # event that, if set, indicates the barber is sleeping
wake_up_barber_event = Event()           # event that, if set, will wake up the barber if they were sleeping

CHAIRS = 4                               # the default capacity of the waiting room
MIN_CUT_TIME = 3                         # the default minimum amount of time a haircut will take
MAX_CUT_TIME = 8                         # the default maximum amount of time a haircut will take

waiting_customers = 0                    # the number of customers in the waiting room


# barber
def barber():
    # add global variables to the local scope of this function
    global barbershop
    global barber_resource
    global mutex
    global waiting_customers
    global MIN_CUT_TIME
    global MAX_CUT_TIME

    mutex.acquire()                        # acquire the mutex to check waiting_customers

    print("{0:%Y-%m-%d %H:%M:%S} - Barber finds {1} customers waiting."
          .format(datetime.datetime.now(), waiting_customers))

    if waiting_customers > 0:
        print("{0:%Y-%m-%d %H:%M:%S} - Barber begins to perform a haircut.".format(datetime.datetime.now()))

        waiting_customers -= 1             # decrement the number of waiting customers

        mutex.release()

        rand_haircut_time = get_random_interval(MIN_CUT_TIME, MAX_CUT_TIME)
        time.sleep(rand_haircut_time)      # Simulate hair cut

        # check to make sure the barber_resource has been acquired before releasing, this prevents an exception
        # from occurring when the barber thread starts while no customers are waiting and therefore trying to
        # acquire the barber_resource
        if not barber_resource.acquire(False):
            barber_resource.release()      # signal that the haircut is complete and the barber is available

        print("{0:%Y-%m-%d %H:%M:%S} - Barber is done performing a haircut.".format(datetime.datetime.now()))
    else:
        mutex.release()                    # didn't need to modify waiting_customers, so release the mutex

        go_to_sleep("{0:%Y-%m-%d %H:%M:%S} - Barber is going to sleep.".format(datetime.datetime.now()))

    if barbershop.acquire(False):
        mutex.acquire()                    # acquire the mutex to check waiting_customers

        if waiting_customers == 0:         # exit if shop is closed and all waiting customers have been served
            mutex.release()
            print("{0:%Y-%m-%d %H:%M:%S} - Done serving customers.".format(datetime.datetime.now()))
            return
        else:                              # serve any remaining customers if the shop has closed
            print("{0:%Y-%m-%d %H:%M:%S} - Barbershop is closed, but {1} customers are still waiting."
                  .format(datetime.datetime.now(), waiting_customers))
            mutex.release()

            # if customers are waiting, release the barbershop so we can check for waiting
            # customers again on the next pass
            barbershop.release()
    barber()


# customer
# customer_number: The number of the customer that has visited the barbershop
def customer(customer_number=0):
    # add global variables to the local scope of this function
    global barber_resource
    global mutex
    global waiting_customers
    global CHAIRS

    mutex.acquire()                                 # acquire the mutex to check waiting_customers
    print("{0:%Y-%m-%d %H:%M:%S} - Customer {1} is entering the store, and finds {2} customer(s) waiting."
          .format(datetime.datetime.now(), customer_number, waiting_customers))
        
    if waiting_customers < CHAIRS:   # if there are waiting room seats available, queue or get a haircut
        wake_up_barber("{0:%Y-%m-%d %H:%M:%S} - Customer {1} is waking up the barber."
                       .format(datetime.datetime.now(), customer_number))

        waiting_customers += 1                      # increment the number of waiting customers

        mutex.release()
        barber_resource.acquire()
        print("{0:%Y-%m-%d %H:%M:%S} - Customer {1} is getting a haircut."
              .format(datetime.datetime.now(), customer_number))
    else:                                           # if no seats are available, customer leaves
        mutex.release()
        print("{0:%Y-%m-%d %H:%M:%S} - Customer {1} could not find an open chair and is leaving."
              .format(datetime.datetime.now(), customer_number))


# get_random_interval
# min_time: The minimum amount of time allowed
# max_time: The maximum amount of time allowed
# return:
# Integer value randomly generated within the range defined by the parameters
def get_random_interval(min_time, max_time):
    rand = Random()                                 # initialize the Random class
    return rand.randint(                            # return a random integer within range
        min_time,
        max_time
    )


# go_to_sleep
# message: The message to print when going to sleep. Can be empty.
def go_to_sleep(message=""):
    global barber_sleeping_event
    global wake_up_barber_event

    if message:
        print(message)

    barber_sleeping_event.set()                     # set the barber state as sleeping
    wake_up_barber_event.wait()                     # block here until the barber is woken

    # clear the event flags so they can be used next time the barber goes to sleep
    wake_up_barber_event.clear()
    barber_sleeping_event.clear()


# go_to_sleep
# message: The message to print when waking up the barber. Can be empty.
def wake_up_barber(message=""):
    global barber_sleeping_event
    global wake_up_barber_event
    global waiting_customers

    if barber_sleeping_event.is_set():              # if the barber is asleep
        if message:
            print(message)

        wake_up_barber_event.set()                  # wake up the barber


def finish_program():
    """Finish the program aggressively without threads cleanup."""
    print('\nYou have pressed Esc key, finishing program...\n')
    os._exit(0)


# main
# args: The parsed command line inputs
# Spawns new customers while the barbershop is open.
def main(args):
    # add global variables to the local scope of this function
    global CHAIRS
    global MIN_CUT_TIME
    global MAX_CUT_TIME

    # parse from args array into global variables, this information is needed in the threads
    CHAIRS = args.seats                     # number of seats in the barbershop
    MIN_CUT_TIME, MAX_CUT_TIME = args.cutrange             # range of time it takes barber to cut hair

    # parse from args array into local variables
    min_customer_time, max_customer_time = args.waitrange  # range of seconds to wait between customer arrivals


    print("{0:%Y-%m-%d %H:%M:%S} - Opening barbershop.".format(datetime.datetime.now()))
    barbershop.acquire()                                   # acquire the barbershop resource for use (open the shop)

    threads = [Thread(target=barber)]                      # add a barber thread to a thread array
    threads[0].start()                                     # start barber thread

    keyboard.add_hotkey('escape', finish_program)          # Finish the program pressing Esc

    customer_number = 0                                    # initialize customer counter
    while True:                            # while program is running
        customer_number += 1                               # increment customer counter
        threads.append(Thread(target=customer,             # add a customer thread
                              args=(customer_number,)))    # need a comma to pass single item into a tuple

        threads[len(threads) - 1].start()                  # start the next customer thread

        rand_sleep_time = get_random_interval(             # get a random time to sleep in range
            min_customer_time,
            max_customer_time
        )

        time.sleep(rand_sleep_time)                        # wait for next customer to arrive

    # for thread in threads:                               # cleanup child threads 
    #     thread.join()                                    # (MUST BE DONE IN THE FUTURE, by not finish aggressively the program or managing an exception)


arguments = 0
if __name__ == "__main__":
    # Set up command line argument parser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description="Run a simulation of the Sleeping Barber's Problem")
    # Interpret -s argument as number of seats in the barbershop
    parser.add_argument('-s', '--seats', type=int, default=4,
                        help="number of seats in barbershop")
    # Interpret -c as how long a haircut will take in seconds (range)
    parser.add_argument('-c', '--cutrange', type=int, default=[3, 8], nargs=2,
                        help="range of times for how long a haircut takes (seconds)")
    # Interpret -w as how long it takes for a new customer to arrive (seconds)
    parser.add_argument('-w', '--waitrange', type=int, default=[1, 6], nargs=2,
                        help="range of times for customer arrivals (seconds)")
    # Assign parsed arguments
    arguments = parser.parse_args()

    # Begin main
    main(arguments)
