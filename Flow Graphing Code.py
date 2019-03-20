"""""
Created on Monday, March 18, 2019
@author: Carlos Doebeli

This script takes the files generated by a flowmeter running on a Blaze instrument and overlays the sets of two dips in 
flow for each flow to determine whether a Blaze instrument is performing acceptably well. 

An instrument is underperforming if any of the following conditions occur: 
    - Flow rate dips to more than 3 mL/min lower than the set flow rate AND less than 40% of the set flow rate
    - Flow rate dips for more than 1s
"""""



#print average flow

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import os
import statistics
from Blaze import Blaze

# This can be used to manually input the series labels instead of reading them from the file

# SERIES = 4
# SERIES_LABELS = ([
#         "1mL Syringe",
#         "3mL Syringe",
#         "5mL Syringe",
#         "10mL Syringe"
#         ])

files = []
path = 'C:/Users/cdoebeli/Documents/Github/Blaze-FAT-code'   # Configure this path each time you use the code
fileNames = []
labels = []
blazes = []
blaze_runs = []

times = []
flow_rates = []


def openFiles():
    for fileName in os.listdir(path):
        if fileName.endswith(".txt"):
            fileNames.append(fileName)
            filePath = path + "/" + fileName
            f = open(filePath, "r")
            files.append(f)


def closeFiles():
    for f in files:
        f.close()


def plot():

    for i in range(0, len(blaze_runs)):
        fig = plt.figure()
        ax = fig.add_subplot(111)

        expected = 0
        median = 0
        resolutions = []
        passfail = "passed"

        for j in range(0, len(blazes)):
            if blazes[j].get_name() is blaze_runs[i] and len(flow_rates[i]) >= 3:
                plt.plot(np.array(blazes[j].get_times()), np.array(blazes[j].get_flow_rates()), '.', label=labels[i],
                         markersize=0.5)
                plt.axhline(y=blazes[j].get_allowable_dip(), linestyle=':', color='r')
                median += blazes[j].get_median_flow()
                expected += blazes[j].get_expected_flow()
                resolutions.append(blazes[j].sample_resolution)
                if not blazes[j].passed():
                    passfail = "passed"

        resolution = statistics.median(resolutions)

        plt.subplots_adjust(top=0.85, right=0.7)
        plt.text(1.05, 0.85, 'matplotlib', transform = ax.transAxes)
        plot_title = name + "_" + str(i+1) + "\n Median flow is: {0:.2f}. Median sample resolution is {1:.3f}s.\nInstrument {2} for flow dips.".format(median, resolution, passfail)
        plot_name = name + "_" + str(i+1)
        if (1 - Blaze.margin_frac()) * expected < median < (1 + Blaze.margin_frac()) * expected and passfail is "passed":
            ax.set_title(plot_title, fontsize='large')
        else:
            ax.set_title(plot_title, color='r', fontsize='large')
        ax.set_xlabel('time (s)')
        ax.set_ylabel('flow rate (mL/min)')
        axbottom, axtop = ax.get_ylim()
        ax.set_ylim(min(axbottom, -0.5), max(axtop, 10))

        fileName = "C:/Users/cdoebeli/Documents/Github/Blaze-FAT-Code/"
        fileName += plot_name + ".png"
        fig.savefig(fileName)

def read_data():
    times.append([])
    flow_rates.append([])

    titled = False

    for line in files[i]:
        data = line.split(';')
        if len(data) == 1 and not titled:
            labels.append(data[0].rstrip("\n\r"))
            titled = True
        elif len(data) >= 2:
            times[i].append(float(data[0]))
            flow_rates[i].append(float(data[1]))

    if not titled:
        labels.append("Series " + str(i + 1))

def get_exp_flow(fileNames, index):
    if index % 2 == 0:
        return 9
    else:
        return 3


openFiles()

for i in range(0, len(files)):
    read_data()



    if i < 2:
        run = "1"
    else:
        run = "2"

    if run not in blaze_runs:
        blaze_runs.append(run)

    exp_flow = get_exp_flow(fileNames, i)
    temp_blaze = Blaze(times[i], flow_rates[i], run, expected_flow=exp_flow)
    blazes.append(temp_blaze)

# print(labels)
name = input("Please enter file name: ")
for blaze in blazes:
    blaze.pass_print()
plot()
closeFiles()


