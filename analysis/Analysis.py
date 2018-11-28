# import sys
# from os import path
# sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from PermutationTest import blocked_sampled_test


class Analysis():

    def __init__(self, 
                 test_statistic,
                 observed_values=[], 
                 unit_assignments=[], 
                 data_path="tmp_data_file.txt"):
        self.test_statistic = test_statistic
        self.observed_values = observed_values
        self.unit_assignments = unit_assignments
        self.data_path = data_path
        self.results = None

    def perform(self):
        self.results = blocked_sampled_test(
            self.observed_values,
            self.unit_assignments,
            self.test_statistic,
            alpha=0.01,
            iterations=10000
        )
    
    def load_data(self):
        unit_assignments = []
        at_unit = False
        at_block = False
        observation = []
        observations = []
        with open(self.data_path, "r") as save_file:
            lines = save_file.readlines()
            for line in lines:
                if at_unit:
                    if "1" in line or "0" in line:
                        assignment = [int(x.strip()) for x in line.split(",") if x.strip() == '1' or x.strip() == '0']
                        if assignment:
                            unit_assignments.append(assignment)
                if at_block:
                    if "isblock" in line:
                        if observation:
                            observations.append(observation)
                            observation = []
                        continue
                    if "1" in line or "0" in line:
                        units = [int(x.strip()) for x in line.split(",") if x.strip() == "1" or x.strip() == "0"]
                        if units:
                            observation.append(units)
                if "unit assignments" in line:
                    at_unit = True
                if "blocks" in line:
                    at_unit = False
                    at_block = True
            if observation:
                observations.append(observation)
        self.unit_assignments = unit_assignments
        self.observed_values = observations
    
    def get_results(self):
        return self.results
