from random import Random
from threading import BoundedSemaphore, Thread

import argparse
import time

# barber
# args: 
# seats_available: the number of seats open at the barber
# cut_done: when the haircut is finished
# close_barber: the semapore controlling whether the barber is open
# min_cut_time: the minimum amount of time it takes for the barber to cut hair
# max_cut_time: the maximum amount of time it takes the barber to cut hair
def barber(seats_available, cut_done, close_barber, min_cut_time, max_cut_time):
    while True:
        try:
            seats_available.release()   # release a seat
            print("Cutting hair")       # cut hair
            # Simulate hair cut
            time.sleep(get_random_interval(min_cut_time, max_cut_time))
            cut_done.release()  # signal that the haircut is finished
        except ValueError:
            # Sleep (do nothing) or exit if shop is closed
            if close_barber.acquire(False):
                break
    print("Barber closed!")


# customer
# args:
# seats_available: the number of seats left open at the barber
# cut_done: the finished haircut
# number: the customer's spot in line
def customer(seats_available, cut_done, number=0):
    print("Customer {} entering store.".format(number))
    if seats_available.acquire(False):
        cut_done.acquire()              # if haircut is finished
        print("Customer {} done getting haircut.".format(number))   # print finished message
    else:   # else all seats are full
        print("Customer {} could not find an open chair and leaves.".format(number))
        return

# get_random_interval
# args:
# min_time: the minimum amount of time allowed
# max_time: the maximum amount of time allowed
# return:
# integer value randomly generated within the parameters
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
    seats_available = BoundedSemaphore(seats)           # initalize seats available
    cut_done = BoundedSemaphore(1)                      # intialize haircuts
    close_barber = BoundedSemaphore(1)                  # intialize barbershop
    cut_done.acquire()                                  # Set cut_done to 0
    close_barber.acquire()                              # Set close_barber to 0
    threads = [Thread(target=barber,                    # init threads
                      args=(seats_available,
                            cut_done,
                            close_barber,
                            min_cut_time,
                            max_cut_time))]
    threads[0].start()                                  # begin threads
    i = 0
    finish = time.time() + barber_duration              # set end simulation time
    while time.time() < finish:                         # while simulation is running
        threads.append(Thread(target=customer,          # add a customer
                              args=(seats_available,
                                    cut_done,
                                    i)))
        threads[len(threads) - 1].start()               # start the next customer
        i += 1                                          # increment counter
        randSleepTime = get_random_interval(            # get a random time to sleep in range
            min_customer_time,
            max_customer_time
        )
        time.sleep(randSleepTime)                       # wait for next customer to arrive
    print("Closing barbershop")     # when simulation time is up
    close_barber.release()          # barbershop closes
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    # Set up command line argument parser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description="Run a simulation of the Sleeping Barber's Problem")
    # interpret -s argument as number of seats in the barbershop
    parser.add_argument('-s', '--seats', type=int, default=3,
                        help="number of seats in barbershop")
    # interpret -d as ow long the barbershop simulation will run in seconds
    parser.add_argument('-d', '--duration', type=int, default=60,
                        help="how long the barbershop is open (seconds)")
    # interpret -c as how long a haircut will take in seconds (range)
    parser.add_argument('-c', '--cutrange', type=int, default=[3, 8], nargs=2,
                        help="range of times for how long a haircut takes (seconds)")
    # interpret -w as how long it takes for a new customer to arrive (seconds)
    parser.add_argument('-w', '--waitrange', type=int, default=[1, 6], nargs=2,
                        help="range of times for customer arrivals (seconds)")
    # assign parsed arguments
    arguments = parser.parse_args()

# begin main
main(arguments)
