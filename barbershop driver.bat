:: Pass in the python interpreter executable path as a command line arg
:: ex. & ".\barbarshop driver.bat" "C:\Program Files (x86)\Microsoft Visual Studio\Shared\Python36_64\python.exe"

@echo off 

:: argument validation
if [%1] == [] (
    echo The file path to the python interpreter python.exe must be provided as an argument when running this script
    exit /B 1
)

if not exist %1 (
    echo The python intrepreter was not found at the path specified: %1 
    exit /B 1
)

:: print a new line
echo.
echo Simulation 1 - Using default parameters
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
