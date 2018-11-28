from __future__ import absolute_import
from six.moves import range
from automation import CommandSequence, TaskManager
from analysis.ProcessData import ProcessData
from copy import copy
from sys import argv
from random import shuffle
import os, shutil


class Stage(object):
    def __init__(self, name, group, site, actions):
        self.name = name
        self.group = group
        self.site = site
        self.actions = actions


class Experiment(object):
    def __init__(self, 
                 num_browsers=10, 
                 num_blocks=1, 
                 feature_extract=None, 
                 data_directory="~/Desktop/",
                 save_path="tmp_data_file.txt",
                 stages=[]):
        self.num_browsers = num_browsers
        self.num_blocks = num_blocks
        self.stages = stages
        self.feature_extract = feature_extract
        self.data_directory = data_directory
        self.save_path = save_path
        self.blocked_data = []
        self.block_assignments = []
        self.manager = self.init_manager()
        self.pd = ProcessData(self.data_directory + "sources/", self.feature_extract)   

    def add_stage(self, name, group, site, action):
        self.stages.append(Stage(name, group, site, action))

    def randomized_assignments(self):
        # map browser index to control/experimental
        browser_indicies = []
        for i in range(self.num_browsers):
            browser_indicies.append(i)
        shuffle(browser_indicies)
        half = int(self.num_browsers / 2)
        assignments = {}
        for i in range(self.num_browsers):
            if i < half:
                # Control
                assignments[browser_indicies[i]] = True
            else:
                # Experimental
                assignments[browser_indicies[i]] = False
        return assignments
    
    def init_manager(self):
        # Loads the manager preference and NUM_BROWSERS copies of the default browser dictionaries
        manager_params, browser_params = TaskManager.load_default_params(self.num_browsers)
        assignments = self.randomized_assignments()
        self.block_assignments.append(assignments)

        # Update browser configuration (use this for per-browser settings)
        for i in range(self.num_browsers):
            # Record HTTP Requests and Responses
            browser_params[i]['http_instrument'] = True
            # Enable flash for all three browsers
            browser_params[i]['disable_flash'] = False
            browser_params[i]['headless'] = True
            browser_params[i]['control'] = assignments[i]

        # Update TaskManager configuration (use this for crawl-wide settings)
        manager_params['data_directory'] = self.data_directory
        manager_params['log_directory'] = '~/Desktop/'

        # Instantiates the measurement platform
        # Commands time out by default after 60 seconds
        try:
            manager = TaskManager.TaskManager(manager_params, browser_params)
        except TypeError:
            raise Exception("Failed to start the manager")
        return manager
    
    def run_once(self):
        for stage in self.stages:
            command_sequence = CommandSequence.CommandSequence(stage.site)
            if isinstance(stage.actions, list):
                for action in stage.actions:
                    action(command_sequence)
            else:
                stage.actions(command_sequence)
            if stage.group == 'experimental':
                self.manager.execute_command_sequence(command_sequence, index='experimental')
            else:
                self.manager.execute_command_sequence(command_sequence, index='**')
        self.manager.close()

    def clean_data_dir(self):
        folder = self.data_directory + "sources/"
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                #elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                print(e)
    
    def run(self):
        self.clean_data_dir()
        self.blocked_data = []
        for _ in range(self.num_blocks):
            self.init_manager()
            self.run_once()
            self.pd.process()
            self.blocked_data.append(self.pd.save_data())
        
    def get_observations(self):
        return self.blocked_data
    
    def get_assignments(self):
        # return self.block_assignments
        assignments = []
        for _ in range(self.num_blocks):
            assignment = [0] * self.num_blocks
            for i in range(self.num_blocks/2):
                assignment[i] = 1
            assignments.append(assignment)
        return assignments
    
    def save_data(self):
        out_str = "unit assignments\n"
        for assignment in self.get_assignments():
            for unit in assignment:
                out_str += str(unit) + ","
            out_str += "\n"
        out_str += "blocks\n"
        for i, block in enumerate(self.blocked_data):
            out_str += "isblock " + str(i + 1) + "\n"
            for observation in block:
                for unit in observation:
                    out_str += str(unit) + ","
                out_str += "\n"
            out_str += "\n"
        with open(self.save_path, "w") as save_file:
            save_file.write(out_str)
