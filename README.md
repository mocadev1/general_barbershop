# Barbershop Problem
## The problem
A barbershop consists of a waiting room with n chairs, and the barber room containing the
barber chair. If there are no customers to be served, the barber goes to sleep. If a customer
enters the barbershop and all chairs are occupied, then the customer leaves the shop. If the
barber is busy, but chairs are available, then the customer sits in one of the free chairs. If the
barber is asleep, the customer wakes up the barber.
## My solution (forked from [alecwest/general_barbershop](https://github.com/alecwest/general_barbershop)) to satisfy my class requirements
`python barbershop.py` runs a default simulation with:
 - 4 seats, 
 - open store until you press Esc key
 - [3, 8] seconds per haircut
 - [1, 6] seconds between customer arrivals

**IMPORTANT, next paragraph belongs to the last commit by alecwest)**
 Also provided is a batch script `barbershop-driver.bat` that runs three basic simulations. Just provide the path to python.exe on your Windows machine as a parameter. 

 ### Arguments
 -  -h, --help
    -   show this help message and exit<br>
 -  -s SEATS, --seats SEATS
    -   number of seats in barbershop (default: 4)
 -  -c CUTRANGE CUTRANGE, --cutrange CUTRANGE CUTRANGE
    -   range of times for how long a haircut takes (seconds) (default: [3, 8])
 -  -w WAITRANGE WAITRANGE, --waitrange WAITRANGE WAITRANGE
    - range of times for customer arrivals (seconds) (default: [1, 6])
