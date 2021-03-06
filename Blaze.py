"""
Created on Monday, March 18, 2019
@author: Carlos Doebeli

This file contains the Blaze class. A Blaze object represents the flow data for one run on a Blaze instrument.
It takes a name, and expected flow, and two arrays of data representing times and flow rates generated by a flowmeter
in its constructor, and uses that information to create lists of data that are more easily understood and viewed,
and is used along with Flow Graphing Code.py to overlay the sets of dips in flow. The Blaze object is a way to store
flow data for multiple runs at the same time, and have it easily accessible.

Note: This file works together with the file Flow Graphing Code.py, and they must be in the same file to work.
"""

import statistics

# Current pass/fail requirements
MARGIN_FRAC = 0.025         # Median flow rate should be within this fraction of the expected flow rate
ALLOWABLE_TIME_S = 0.8      # Maximum allowable dip time, in seconds
MAX_DIP_ABS = 4             # Largest allowable absolute dip, in mL/min
MAX_DIP_FRAC = 0.6          # Minimum acceptable fractional dip compared to the expected flow rate
# IF THE CODE DOES NOT WORK AS EXPECTED AND THE FLOW DROPS ARE TOO SMALL, CHANGE THE RANGE TO BE SMALLER.
RANGE = 0.2                 # The range for determining a dip has occurred. If a value is within this fraction of the expected TFR, it is in the range
THRESHOLD_TIME = 10         # Time, in seconds, to determine when steady flow has been reached. About 1/3 of the expected period


class Blaze:

    # Returns whether a value is within 20% of the expected value
    @staticmethod
    def in_range(expected_flow_rate, value):
        return (1 - RANGE) * expected_flow_rate < value < (1 + RANGE) * expected_flow_rate

    @staticmethod
    def margin_frac():
        return MARGIN_FRAC

    def __init__(self, raw_times, raw_flow_rates, run_name, expected_flow=9):
        # Initial data points and identifiers
        self.raw_times = raw_times
        self.raw_flow_rates = raw_flow_rates
        self.expected_flow_rate = expected_flow
        self.name = run_name

        self.threshold_time = THRESHOLD_TIME
        self.allowable_time = ALLOWABLE_TIME_S

        # Initialize data values before they are calculated
        self.ignore_times = None
        self.max_dip_time = None
        self.period = None
        self.lower_bound = None
        self.upper_bound = None

        # Find data points within a range, and generate the data to be graphed
        self.times, self.flow_rates = self._generate_data()
        self.graph_times, self.graph_flow_rates = self._graphing_data()

        length = len(self.raw_times)
        self.sample_resolution = self.raw_times[length - 1] / length
        self.raw_median = statistics.median(raw_flow_rates)
        self.median_flow = statistics.median(self.graph_flow_rates)
        self.minimum_dip = min(self.graph_flow_rates)
        self.allowable_dip = min(float(self.expected_flow_rate - MAX_DIP_ABS), self.expected_flow_rate * MAX_DIP_FRAC)
        self.passes = self.passed()

        # Print statements for debugging
        # print(self.median_flow)
        # print(self.max_dip_time)
        # print(self.minimum_dip)
        # print("")

    def get_name(self):
        return self.name

    def get_expected_flow(self):
        return self.expected_flow_rate

    # Returns the times to be graphed
    def get_times(self):
        return self.graph_times.copy()

    # Returns the flow rates to be graphed
    def get_flow_rates(self):
        return self.graph_flow_rates.copy()

    # Returns the data to be graphed
    def get_graph_data(self):
        return self.graph_times.copy(), self.graph_flow_rates.copy()

    # Returns the raw data
    def get_raw_data(self):
        return self.raw_times.copy(), self.raw_flow_rates.copy()

    # Returns the data in between the lower and upper bounds
    def get_steadystate_data(self):
        return self.times.copy(), self.flow_rates.copy()

    def get_time_resolution(self):
        return self.sample_resolution

    def get_median_flow(self):
        return self.median_flow

    def get_minimum_dip(self):
        return self.minimum_dip

    def get_allowable_dip(self):
        return self.allowable_dip

    def get_max_dip_time(self):
        return self.max_dip_time

    # Public method that prints the success or failure status of the dip magnitude and dip times
    def pass_print(self):
        print("For Blaze run {0} at a flow rate of {1} mL/min: ".format(self.name, self.expected_flow_rate))
        if self.passes:
            passfail = "PASSED"
        else:
            passfail = "FAILED"
        print("Overall: " + passfail)
        if self.minimum_dip < self.allowable_dip:
            print("Dip magnitude failed.")
            print("Minimum dip is: {0}: ".format(self.minimum_dip))
            print("Allowable dip is: {0}: \n".format(self.allowable_dip))
        else:
            print("Dip time passed.")
            print("Minimum dip is: {0}: ".format(self.minimum_dip))
            print("Allowable dip is: {0} \n".format(self.allowable_dip))

        if self.max_dip_time > self.allowable_time:
            print("Dip time failed.")
            print("Maximum dip time is: {0}: ".format(self.max_dip_time))
            print("Allowable dip time is: {0}: ".format(self.allowable_time))
        else:
            print("Dip time passed.")
            print("Maximum dip time is: {0}: ".format(self.max_dip_time))
            print("Allowable dip time is: {0} ".format(self.allowable_time))
        print("\n")

    # Public method to determine whether the instrument run has passed according to the dips
    def passed(self):
        return self.minimum_dip > self.allowable_dip and self.max_dip_time < self.allowable_time

    # Public method to determine whether the largest dip magnitude is acceptable
    def pass_dip_magnitude(self):
        return self.minimum_dip > self.allowable_dip

    # Public method to determine whether the maximum dip time is acceptable
    def pass_max_dip_time(self):
        return self.max_dip_time < self.allowable_time

    # Method to generate the data in between the upper and lower bounds given raw data
    def _generate_data(self):
        temp_times = []
        temp_flow_rates = []

        self.lower_bound, self.upper_bound = self._get_bounds()

        for i in range(0, len(self.raw_times)):
            if self.lower_bound < self.raw_times[i] < self.upper_bound:
                temp_times.append((self.raw_times[i] - self.lower_bound))
                temp_flow_rates.append(self.raw_flow_rates[i])

        return temp_times.copy(), temp_flow_rates.copy()

    # Method to find the lower bound, upper bound, period, and maximum dip time
    # Returns the lower bound and upper bound. The period and maximum dip time are changed in the method
    def _get_bounds(self):
        upper_index, upper_bound = self._get_upper_bound()
        lower_index, lower_bound = self._get_lower_bound(upper_index)
        self._get_period(lower_index, upper_index)
        return lower_bound, upper_bound

    # Method to find the average period of how long it takes for two dips to occur
    # Stores the times of the past three dips and calculates the length of time between two dips
    def _get_period(self, lower_index, upper_index):
        prev_time = 0
        curr_time = 0
        new_time = 0
        dip_periods = []
        self.ignore_times = []
        self.max_dip_time = 0

        for i in range(lower_index, upper_index):
            if Blaze.in_range(self.expected_flow_rate, self.raw_flow_rates[i - 1]) and not Blaze.in_range(self.expected_flow_rate, self.raw_flow_rates[i]):
                prev_time = curr_time
                curr_time = new_time
                new_time = self.raw_times[i]
                if prev_time is not 0:
                    dip_periods.append(new_time - prev_time)

            if Blaze.in_range(self.expected_flow_rate, self.raw_flow_rates[i]) and self.raw_flow_rates[i - 1] <= 0.8 * self.expected_flow_rate:
                if new_time is not 0:
                    dip_time = self.raw_times[i] - new_time
                    self.max_dip_time = max(dip_time, self.max_dip_time)

            if self.raw_flow_rates[i] > 1.2 * self.expected_flow_rate:
                self.ignore_times.append(self.raw_times[i] - self.raw_times[lower_index])

        if dip_periods:
            self.period = statistics.median(dip_periods)

    # Finds the lower bound of the steady state flow
    # Upper index is passed to be safe in the case of no dips occurring
    def _get_lower_bound(self, upper_index):
        lower_index = 0
        lower_bound = 0
        i = 0

        while i < len(self.raw_times) and lower_bound == 0:
            if Blaze.in_range(self.expected_flow_rate, self.raw_flow_rates[i]):
                j = i
                while self.raw_times[j] - self.raw_times[i] < self.threshold_time:
                    if Blaze.in_range(self.expected_flow_rate, self.raw_flow_rates[j]):
                        j += 1
                    else:
                        i = j
                        break

                if self.raw_times[j] - self.raw_times[i] >= self.threshold_time:
                    lower_index = i
                    lower_bound = self.raw_times[i]
            i += 1

        # Finds the point just after the first dip, if there is a dip. If there are no dips until the already-calculated
        # upper bound, then the first lower bound will be taken
        if lower_bound is not 0:
            while Blaze.in_range(self.expected_flow_rate, self.raw_flow_rates[i]) and i < upper_index:
                i += 1
            while not Blaze.in_range(self.expected_flow_rate, self.raw_flow_rates[i]) and i < upper_index:
                i += 1
            if i is not upper_index:
                lower_index = i
                lower_bound = self.raw_times[i]

        return lower_index, lower_bound

    # Finds the upper bound of the steady state flow
    def _get_upper_bound(self):
        upper_index = 0
        upper_bound = 0

        i = len(self.raw_times) - 1
        while i >= 0 and upper_bound == 0:
            if Blaze.in_range(self.expected_flow_rate, self.raw_flow_rates[i]):
                j = i
                while self.raw_times[i] - self.raw_times[j] < self.threshold_time:
                    if Blaze.in_range(self.expected_flow_rate, self.raw_flow_rates[j]):
                        j -= 1
                    else:
                        i = j
                        break

                if self.raw_times[i] - self.raw_times[j] >= self.threshold_time:
                    upper_index = j
                    upper_bound = self.raw_times[j]
            i -= 1

        return upper_index, upper_bound

    # Uses the data between the lower and upper bound and overlays the sets of two dips according to the calculated period
    def _graphing_data(self):
        temp_times = []
        temp_flow_rates = []

        for i in range(0, len(self.times)):
            if not self._ignored(self.times[i]):
                if self.period:
                    temp_times.append((self.times[i] + 3 * self.period / 4) % self.period)
                else:
                    temp_times.append(self.times[i])
                temp_flow_rates.append(self.flow_rates[i])
        return temp_times.copy(), temp_flow_rates.copy()

    # Method to determine whether a value should be ignored due to air bubble errors
    def _ignored(self, value):
        if self.period:
            time_interval = self.period / 2
        else:
            time_interval = 5
        for x in self.ignore_times:
            if abs(x - value) < time_interval:
                return True
        return False
