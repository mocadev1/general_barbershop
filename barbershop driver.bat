:: Pass in the python interpreter executable path as a command line arg
:: ex. "C:\Program Files (x86)\Microsoft Visual Studio\Shared\Python36_64\python.exe"

@echo off 

set interpreterPath = %1

echo Simulation 1 - Using default parameters
:: print a new line
echo.
%1 barbershop.py 

echo.
echo Simulation 2 - 1 second between each customer arrival
echo.
%1 barbershop.py -c 3 8 -w 1 1

echo.
echo Simulation 3 - 1 second haircut time
echo.
%1 barbershop.py -c 1 1 -w 1 6
