# Round Robin Scheduler

## Needed libs to run the scheduler

- Numpy: Used to generate random colors in the Gantt's chart, also needed to show the timestamp in the y axis of the chart

- Matplotlib: Used to generate the values and animations on real time in Gantt's chart

## How to install the libs

To install, just run the follow command in terminal:

"pip install numpy, matplotlib"

If you don't have the pip package manager installed, run this command:

"python -m ensurepip --default-pip"

## How to run the scheduler

There is a file called "arquivo_teste.txt" inside it there are 4 columns, first one is the name of the process, second one is the duration of the process in the CPU, the third column is the time of arrival of the process in the CPU, and the last one is reserved for I/O operation time, which could be separated with commas.

This file have some example values but you can change it with your values to test the scheduler.

To run the code, you can use a terminal or some IDE, like VSCode.

To run in terminal:

cd "FOLDER PATH"

"python main.py"
