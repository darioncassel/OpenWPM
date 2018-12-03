import os

class ProcessData():

    def __init__(self, sources_dir, feature_extract):
        self.sources_dir = sources_dir
        self.feature_extract = feature_extract

    def read_files(self):
        experimental_lines = []
        control_lines = []
        for filename in os.listdir(self.sources_dir):
            with open(self.sources_dir + filename, 'r') as data_file:
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
    
    def generate_total_feature_matrix(self, features_e, features_c):
        all_topics = []
        for tl in features_e:
            for t in tl:
                if t not in all_topics:
                    all_topics.append(t)
        for tl in features_c:
            for t in tl:
                if t not in all_topics:
                    all_topics.append(t)
        total_matrix = []
        for tl in features_e:
            vec = [0] * len(all_topics)
            for t in tl:
                i = all_topics.index(t)
                vec[i] = 1
            total_matrix.append(vec)
        for tl in features_c:
            vec = [0] * len(all_topics)
            for t in tl:
                i = all_topics.index(t)
                vec[i] = 1
            total_matrix.append(vec)
        return all_topics, total_matrix
    
    def process(self):
        experimental_observations, control_observations = self.read_files()
        self.features_e, self.features_c = self.extract_features(experimental_observations, control_observations)
        self.all_topics, self.feature_matrix = self.generate_total_feature_matrix(features_e, features_c)
    
    def save_data(self):
        return self.features_e, self.features_c, self.all_topics, self.feature_matrix
