# import sys
# from os import path
# sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from PermutationTest import blocked_sampled_test


class Analysis():

    def __init__(self, observed_values, unit_assignments, test_statistic):
        self.observed_values = observed_values
        self.unit_assignments = unit_assignments
        self.test_statistic = test_statistic
        self.results = None

    def perform(self):
        self.results = blocked_sampled_test(
            self.observed_values,
            self.unit_assignments,
            self.test_statistic,
            alpha=0.01,
            iterations=10000
        )
    
    def get_results(self):
        return self.results
