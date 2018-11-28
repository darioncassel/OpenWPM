import os

class Analysis():

    def __init__(self, sources_dir, feature_extract, test_statistic):
        self.sources_dir = sources_dir
        self.feature_extract = feature_extract
        self.test_statistic = test_statistic
        self.features, self.mat_e, self.mat_c = self.process_data()

    def read_files(self):
        experimental_lines = []
        control_lines = []
        for filename in os.listdir(self.sources_dir):
            with open(self.sources_dir + "/" + filename, 'r') as data_file:
                if "control" in filename:
                    control_lines.append(data_file.readlines())
                else:
                    experimental_lines.append(data_file.readlines())
        return experimental_lines, control_lines
    
    def extract_features(self, experimental_observations, control_observations):
        processed_exp = []
        processed_con = []
        for l in experimental_observations:
            processed_exp.append(self.feature_extract(l))
        for l in control_observations:
            processed_con.append(self.feature_extract(l))
        return processed_exp, processed_con
    
    def generate_feature_matrix(self, features_e, features_c):
        all_topics = []
        for tl in features_e:
            for t in tl:
                if t not in all_topics:
                    all_topics.append(t)
        for tl in features_c:
            for t in tl:
                if t not in all_topics:
                    all_topics.append(t)
        exp_matrix = []
        for tl in features_e:
            vec = [0] * len(all_topics)
            for t in tl:
                i = all_topics.index(t)
                vec[i] = 1
            exp_matrix.append(vec)
        con_matrix = []
        for tl in features_c:
            vec = [0] * len(all_topics)
            for t in tl:
                i = all_topics.index(t)
                vec[i] = 1
            con_matrix.append(vec)
        return all_topics, exp_matrix, con_matrix
    
    def process_data(self):
        experimental_observations, control_observations = self.read_files()
        features_e, features_c = self.extract_features(experimental_observations, control_observations)
        features, mat_e, mat_c, = self.generate_feature_matrix(features_e, features_c)
        return features, mat_e, mat_c

    def perform(self):
        self.test_statistic(self.features, self.mat_e, self.mat_c)
    
    def save_data(self):
        return self.features, self.mat_e, self.mat_c
