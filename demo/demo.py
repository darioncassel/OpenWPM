from __future__ import absolute_import
from demo_util import *
from sys import argv


NUM_BROWSERS = 2
NUM_BLOCKS = 2
TEST_NAME = "demo"


def run_experiment(data_directory, num_browsers=20, num_blocks=10):
    persona = Experiment(
        data_directory=data_directory,
        num_browsers=num_browsers,
        num_blocks=num_blocks,
        feature_extract=extract_topics,
        save_path=TEST_NAME + "_data.txt"
    )
    persona.add_stage(
        "start", "all", "https://www.youtube.com/",
        [visit, scroll]
    )
    persona.add_stage(
        "treatment", "experimental", "https://www.google.com/", 
        [visit]
    )
    persona.add_stage(
        "measurement", "all", "https://www.youtube.com/", 
        [visit, scroll, save_page_source]
    )
    persona.run()
    persona.save_data()
    return persona.get_observations(), persona.get_assignments()

def run_analysis(observations, assignments):
    analysis = Analysis(
        observed_values=observations,
        unit_assignments=assignments,
        test_statistic=test_statistic,
        save_path=TEST_NAME + "_results.txt"
    )
    analysis.perform()
    analysis.save_results()
    return analysis.get_results()

def main():
    data_directory = "/home/vagrant/Desktop/"
    observations, assignments = run_experiment(data_directory, NUM_BROWSERS, NUM_BLOCKS)
    results = run_analysis(observations, assignments)
    print "p-value: %f" % results


if __name__ == "__main__":
    if __package__ is None:
        import sys
        from os import path
        sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
        from experiment.Experiment import Experiment, Stage
        from analysis.Analysis import Analysis
    else:
        from ..experiment.Experiment import Experiment, Stage
        from ..analysis.Analysis import Analysis
    main()
