#
#make note of median
#make note of sample resolution

import statistics

RED = "\033[1;31m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"

MARGIN_FRAC = 0.025
ALLOWABLE_TIME_S = 0.8
MAX_DIP_ABS = 4
MAX_DIP_FRAC = 0.6


class Blaze:

    @staticmethod
    def in_range(expected_flow_rate, value):
        return 0.8 * expected_flow_rate < value < 1.2 * expected_flow_rate

    @staticmethod
    def margin_frac():
        return MARGIN_FRAC

    def __init__(self, raw_times, raw_flow_rates, run_name, expected_flow=9, threshold_time=10):
        self.raw_times = raw_times
        self.raw_flow_rates = raw_flow_rates
        self.expected_flow_rate = expected_flow
        self.name = run_name

        self.threshold_time = threshold_time

        self.ignore_times = None
        self.max_dip_time = None
        self.allowable_time = ALLOWABLE_TIME_S
        self.period = None
        self.lower_bound = None
        self.upper_bound = None

        self.times, self.flow_rates = self._generate_data()
        self.graph_times, self.graph_flow_rates = self._graphing_data()

        length = len(self.raw_times)
        self.sample_resolution = self.raw_times[length - 1] / length
        # should be within 2.5%
        self.median_flow = statistics.median(self.graph_flow_rates)
        self.minimum_dip = min(self.graph_flow_rates)
        self.allowable_dip = min(float(self.expected_flow_rate - MAX_DIP_ABS), self.expected_flow_rate * MAX_DIP_FRAC)
        self.passes = self.passed()

        print(self.median_flow)
        print(self.max_dip_time)
        print(self.minimum_dip)
        print("")

    def get_name(self):
        return self.name

    def get_expected_flow(self):
        return self.expected_flow_rate

    def get_times(self):
        return self.graph_times.copy()

    def get_flow_rates(self):
        return self.graph_flow_rates.copy()

    def get_graph_data(self):
        return self.graph_times.copy(), self.graph_flow_rates.copy()

    def get_raw_data(self):
        return self.raw_times.copy(), self.raw_flow_rates.copy()

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

    def passed(self):
        return self.minimum_dip > self.allowable_dip and self.max_dip_time < self.allowable_time

    def pass_dip_magnitude(self):
        return self.minimum_dip > self.allowable_dip

    def pass_max_dip_time(self):
        return self.max_dip_time < self.allowable_time

    def _generate_data(self):
        temp_times = []
        temp_flow_rates = []

        self.lower_bound, self.upper_bound = self._get_bounds()

        for i in range(0, len(self.raw_times)):
            if self.lower_bound < self.raw_times[i] < self.upper_bound:
                temp_times.append((self.raw_times[i] - self.lower_bound))
                temp_flow_rates.append(self.raw_flow_rates[i])

        return temp_times.copy(), temp_flow_rates.copy()

    def _get_bounds(self):
        upper_index, upper_bound = self._get_upper_bound()
        lower_index, lower_bound = self._get_lower_bound(upper_index)
        self._get_period(lower_index, upper_index)
        return lower_bound, upper_bound

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

        if lower_bound is not 0:
            while Blaze.in_range(self.expected_flow_rate, self.raw_flow_rates[i]) and i < upper_index:
                i += 1
            while not Blaze.in_range(self.expected_flow_rate, self.raw_flow_rates[i]) and i < upper_index:
                i += 1
            if i is not upper_index:
                lower_index = i
                lower_bound = self.raw_times[i]

        return lower_index, lower_bound

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

    def _ignored(self, value):
        if self.period:
            time_interval = self.period / 2
        else:
            time_interval = 5
        for x in self.ignore_times:
            if abs(x - value) < time_interval:
                return True
        return False
