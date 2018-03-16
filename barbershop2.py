from random import Random
from threading import BoundedSemaphore, Thread

import argparse
import time
import datetime


# barber
# args: 
# waiting_room: The semaphore controlling access to the waiting room
# barber_resource: The semaphore controlling access to the barber
# barbershop: The semaphore controlling access to the barbershop resource
# min_cut_time: The minimum amount of time it takes for the barber to cut hair
# max_cut_time: The maximum amount of time it takes the barber to cut hair
def barber(waiting_room, barber_resource, barbershop, min_cut_time, max_cut_time):
    while True:
        # print("Barber is awake")
        try:
            waiting_room.release()       # release a seat in the waiting room
            barber_resource.release()      # signal that the haircut is in progress and the barber is not available (1)

            rand_haircut_time = get_random_interval(min_cut_time, max_cut_time)

            print("{0:%Y-%m-%d %H:%M:%S} Waiting {1} seconds for haircut to complete"
                  .format(datetime.datetime.now(), rand_haircut_time))
            time.sleep(rand_haircut_time)  # Simulate hair cut
        except ValueError:
            # Sleep (do nothing) or exit if shop is closed
            if barbershop.acquire(False):
                break
    print("{0:%Y-%m-%d %H:%M:%S} Barber is asleep".format(datetime.datetime.now()))


# customer
# args:
# waiting_room: The semaphore controlling access to the waiting room
# barber_resource: The semaphore controlling access to the barber
# number: The customer's spot in line
def customer(waiting_room, barber_resource, number=0):
    print("{0:%Y-%m-%d %H:%M:%S} Customer {1} is entering the store.".format(datetime.datetime.now(), number))
    if waiting_room.acquire(False):
        barber_resource.acquire()        # signal that the haircut is finished and the barber is available (0)
        print("{0:%Y-%m-%d %H:%M:%S} Customer {1} is getting a haircut.".format(datetime.datetime.now(), number))
    else:   # else all seats are full
        print("{0:%Y-%m-%d %H:%M:%S} Customer {1} could not find an open chair and is leaving."
              .format(datetime.datetime.now(), number))
        return


# get_random_interval
# args:
# min_time: The minimum amount of time allowed
# max_time: The maximum amount of time allowed
# return:
# Integer value randomly generated within the range defined by the parameters
def get_random_interval(min_time, max_time):
    rand = Random()         # initialize the Random class
    return rand.randint(   # return a random integer within range
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

    waiting_room = BoundedSemaphore(seats)  # initialize semaphore that indicates if waiting room seats are available
    barber_resource = BoundedSemaphore(1)   # initialize semaphore that indicates if the barber is available
    barbershop = BoundedSemaphore(1)        # initialize semaphore that indicates if the barbershop is available

    print("{0:%Y-%m-%d %H:%M:%S} Opening barbershop".format(datetime.datetime.now()))
    barbershop.acquire()                    # acquire the barbershop resource for use (open the shop) (0)

    threads = [Thread(target=barber,                 # initialize barber thread
                      args=(waiting_room,
                            barber_resource,
                            barbershop,
                            min_cut_time,
                            max_cut_time))]
    threads[0].start()                               # start barber thread

    i = 0                                            # initialize thread counter
    while time.time() < finish:                      # while simulation is running
        threads.append(Thread(target=customer,       # add a customer thread
                              args=(waiting_room,
                                    barber_resource,
                                    i)))
        threads[len(threads) - 1].start()            # start the next customer thread

        i += 1                                       # increment customer counter
        rand_sleep_time = get_random_interval(       # get a random time to sleep in range
            min_customer_time,
            max_customer_time
        )

        print("{0:%Y-%m-%d %H:%M:%S} Waiting {1} seconds for next customer"
              .format(datetime.datetime.now(), rand_sleep_time))
        time.sleep(rand_sleep_time)                  # wait for next customer to arrive

    print("{0:%Y-%m-%d %H:%M:%S} Closing barbershop".format(datetime.datetime.now()))     # when simulation time is up
    barbershop.release()            # release the barbershop resource (close the shop) (1)
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
    parser.add_argument('-d', '--duration', type=int, default=30,
                        help="how long the barbershop is open (seconds)")
    # parser.add_argument('-d', '--duration', type=int, default=60,
    #                     help="how long the barbershop is open (seconds)")
    # Interpret -c as how long a haircut will take in seconds (range)
    parser.add_argument('-c', '--cutrange', type=int, default=[3, 8], nargs=2,
                        help="range of times for how long a haircut takes (seconds)")
    # parser.add_argument('-c', '--cutrange', type=int, default=[1, 1], nargs=2,
    #                     help="range of times for how long a haircut takes (seconds)")
    # Interpret -w as how long it takes for a new customer to arrive (seconds)
    parser.add_argument('-w', '--waitrange', type=int, default=[1, 6], nargs=2,
                        help="range of times for customer arrivals (seconds)")
    # Assign parsed arguments
    arguments = parser.parse_args()

# Begin main
main(arguments)
