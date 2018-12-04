from sys import maxint
import numpy as np
from PermutationTest import blocked_sampled_test
import pickle


class Analysis():

    def __init__(self, 
                 test_statistic,
                 observed_values=[], 
                 unit_assignments=[],
                 truncate = -1,
                 data_path="tmp_data_file.txt",
                 save_path="results.txt"):
        self.test_statistic = test_statistic
        self.observed_values = observed_values
        self.unit_assignments = unit_assignments
        self.data_path = data_path
        self.save_path = save_path
        self.results = None
        self.truncate = truncate

    def perform(self):
        self.truncate_data(self.truncate)
        self.size_data()
        observed_values = []
        for block in self.observed_values:
            np_block = []
            for observation in block:
                np_block.append(np.array(observation))
            observed_values.append(np.array(np_block))
        np_observed_values = np.array(observed_values)
        np_unit_assignments = np.array([np.array(x) for x in self.unit_assignments])
        results = blocked_sampled_test(
            np_observed_values,
            np_unit_assignments,
            self.test_statistic,
            alpha=0.01,
            iterations=10000
        )
        self.results = results
    
    def load_data(self):
        with open(self.data_path, "r") as save_file:
            data = pickle.load(save_file)
            self.unit_assignments = data["unit_assignments"]
            self.observed_values = data["observed_values"]
    
    def truncate_data(self, k=-1):
        new_observed_values = []
        if k > 0:
            for data in self.observed_values:
                features_e = data["features_e"]
                features_c = data["features_c"]
                all_features = []
                for tl in features_e:
                    for t in tl[:k]:
                        if t not in all_features:
                            all_features.append(t)
                for tl in features_c:
                    for t in tl[:k]:
                        if t not in all_features:
                            all_features.append(t)
                total_matrix = []
                for tl in features_e:
                    vec = [0] * len(all_features)
                    for t in tl[:k]:
                        i = all_features.index(t)
                        vec[i] = 1
                    total_matrix.append(vec)
                for tl in features_c:
                    vec = [0] * len(all_features)
                    for t in tl[:k]:
                        i = all_features.index(t)
                        vec[i] = 1
                    total_matrix.append(vec)
                new_observed_values.append(total_matrix)
        else:
            for data in self.observed_values:
                block = data["feature_matrix"]
                new_observed_values.append(block)
        self.observed_values = new_observed_values

    def size_data(self):
        min_len = maxint
        for observation in self.observed_values:
            ob_len = len(observation[0])
            if ob_len < min_len:
                min_len = ob_len
        new_observations = []
        for observation in self.observed_values:
            new_observation = []
            for unit in observation:
                new_observation.append(unit[:min_len])
            new_observations.append(new_observation)
        self.observed_values = new_observations
    
    def get_results(self):
        return self.results

    def save_results(self):
        with open(self.save_path, "w") as save_file:
            save_file.write("p-value: " + str(self.results) + "\n")
