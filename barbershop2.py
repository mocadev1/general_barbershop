from random import Random
from threading import BoundedSemaphore, Thread

import argparse
import time
import datetime

barbershop = BoundedSemaphore(1)         # semaphore that indicates if the barbershop is available
barber_resource = BoundedSemaphore(1)    # semaphore that indicates if the barber is available
mutex = BoundedSemaphore(1)              # semaphore that insures exclusive access to the customers variable

max_waiting_customers = 3                # the default capacity of the waiting room
min_cut_time = 1                         # the default minimum amount of time a haircut will take
max_cut_time = 1                         # the default maximum amount of time a haircut will take

waiting_customers = 0                    # the number of customers in the waiting room


# barber
def barber():
    # add global variables to the local scope of this function
    global barbershop
    global barber_resource
    global mutex
    global waiting_customers
    global min_cut_time
    global max_cut_time

    while True:
        # print("{0} Barber is awake".format(datetime.datetime.now()))  # No string formatting for a precise time output

        if waiting_customers > 0:
            mutex.acquire()
            waiting_customers -= 1
            mutex.release()

            rand_haircut_time = get_random_interval(min_cut_time, max_cut_time)
            # print("Barber: Haircut time is {0}".format(rand_haircut_time))
            time.sleep(rand_haircut_time)      # Simulate hair cut

            # check to make sure the barber_resource has been acquired before releasing, this prevents an exception
            # from occurring when the barber thread starts while no customers are waiting and therefore trying to
            # acquire the barber_resource
            if not barber_resource.acquire(False):
                barber_resource.release()      # signal that the haircut is complete and the barber is available

            print("{0:%Y-%m-%d %H:%M:%S} - Done performing a haircut".format(datetime.datetime.now()))
        else:
            time.sleep(1)
            # TODO: This is still busy waiting, but only updates each second now.  My attempts to eliminate busy
            # waiting have not been successful so far, adding another semaphore to get the barber to block until a
            # customer is available for a haircut has not been a simple task as it causes other issues. I may meet with
            # the professor to discuss this. -Patrick

        if barbershop.acquire(False):
            if waiting_customers == 0:     # exit if shop is closed and all waiting customers have been served
                print("{0:%Y-%m-%d %H:%M:%S} - Done serving customers".format(datetime.datetime.now()))
                break
            else:
                print("{0:%Y-%m-%d %H:%M:%S} - Barbershop is closed, but {1} customers are still waiting"
                      .format(datetime.datetime.now(), waiting_customers))
                barbershop.release()


# customer
# customer_number: The number of the customer that has visited the barbershop
def customer(customer_number=0):
    # add global variables to the local scope of this function
    global barber_resource
    global mutex
    global waiting_customers
    global max_waiting_customers

    print("{0:%Y-%m-%d %H:%M:%S} - Customer {1} is entering the store."
          .format(datetime.datetime.now(), customer_number))
    mutex.acquire()

    if waiting_customers < max_waiting_customers:
        waiting_customers += 1

        mutex.release()
        barber_resource.acquire()
        print("{0:%Y-%m-%d %H:%M:%S} - Customer {1} is getting a haircut."
              .format(datetime.datetime.now(), customer_number))
    else:
        mutex.release()
        print("{0:%Y-%m-%d %H:%M:%S} - Customer {1} could not find an open chair and is leaving."
              .format(datetime.datetime.now(), customer_number))


# get_random_interval
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
# Closes barbershop when the specified time limit has elapsed.
def main(args):
    # add global variables to the local scope of this function
    global max_waiting_customers
    global min_cut_time
    global max_cut_time

    # parse from args array into global variables, this information is needed in the threads
    max_waiting_customers = args.seats                     # number of seats in the barbershop
    min_cut_time, max_cut_time = args.cutrange             # range of time it takes barber to cut hair

    # parse from args array into local variables
    barber_duration = args.duration                        # number of seconds to run simulation
    min_customer_time, max_customer_time = args.waitrange  # range of seconds to wait between customer arrivals

    finish = time.time() + barber_duration                 # set end simulation time

    print("{0:%Y-%m-%d %H:%M:%S} - Opening barbershop".format(datetime.datetime.now()))
    barbershop.acquire()                                   # acquire the barbershop resource for use (open the shop)

    threads = [Thread(target=barber)]                      # add a barber thread to a thread array
    threads[0].start()                                     # start barber thread

    customer_number = 0                                    # initialize customer counter
    while time.time() < finish:                            # while simulation is running
        customer_number += 1                               # increment customer counter
        threads.append(Thread(target=customer,             # add a customer thread
                              args=(customer_number,)))    # need a comma to pass single item into a tuple

        threads[len(threads) - 1].start()                  # start the next customer thread

        rand_sleep_time = get_random_interval(             # get a random time to sleep in range
            min_customer_time,
            max_customer_time
        )

        time.sleep(rand_sleep_time)                        # wait for next customer to arrive

    print("{0:%Y-%m-%d %H:%M:%S} - Closing barbershop".format(datetime.datetime.now()))  # when simulation time is up
    barbershop.release()                                   # release the barbershop resource (close the shop)

    for thread in threads:                                 # cleanup child threads
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
    parser.add_argument('-d', '--duration', type=int, default=15,
                        help="how long the barbershop is open (seconds)")
    # parser.add_argument('-d', '--duration', type=int, default=60,
    #                     help="how long the barbershop is open (seconds)")
    # Interpret -c as how long a haircut will take in seconds (range)
    # parser.add_argument('-c', '--cutrange', type=int, default=[3, 8], nargs=2,
    #                     help="range of times for how long a haircut takes (seconds)")
    parser.add_argument('-c', '--cutrange', type=int, default=[1, 1], nargs=2,
                        help="range of times for how long a haircut takes (seconds)")
    # Interpret -w as how long it takes for a new customer to arrive (seconds)
    parser.add_argument('-w', '--waitrange', type=int, default=[1, 6], nargs=2,
                        help="range of times for customer arrivals (seconds)")
    # parser.add_argument('-w', '--waitrange', type=int, default=[1, 1], nargs=2,
    #                     help="range of times for customer arrivals (seconds)")
    # Assign parsed arguments
    arguments = parser.parse_args()

# Begin main
main(arguments)
