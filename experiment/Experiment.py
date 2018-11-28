from __future__ import absolute_import
from six.moves import range
from automation import CommandSequence, TaskManager
from analysis.ProcessData import ProcessData
from copy import copy
from sys import argv
from random import shuffle


class Stage(object):
    def __init__(self, name, group, site, actions):
        self.name = name
        self.group = group
        self.site = site
        self.actions = actions


class Experiment(object):
    def __init__(self, num_browsers=10, num_blocks=1, feature_extract=None, data_directory="~/Desktop/", stages=[]):
        self.num_browsers = num_browsers
        self.num_blocks = num_blocks
        self.stages = stages
        self.feature_extract = feature_extract
        self.data_directory = data_directory
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
        manager = TaskManager.TaskManager(manager_params, browser_params)
        return manager
    
    def run_once(self):
        for stage in self.stages:
            command_sequence = CommandSequence.CommandSequence(stage.site)
            if isinstance(stage.actions, list):
                for action in stage.actions:
                    action(command_sequence)
            else:
                stage.actions(command_sequence)
            if stage.group == 'control':
                self.manager.execute_command_sequence(command_sequence, index='control')
            else:
                self.manager.execute_command_sequence(command_sequence, index='**')
        self.manager.close()
    
    def run(self):
        self.blocked_data = []
        for _ in range(self.num_blocks):
            self.init_manager()
            self.run_once()
            self.pd.process()
            self.blocked_data.append(self.pd.save_data())
        
    def get_observations(self):
        return self.blocked_data
    
    def get_assignments(self):
        assignments = []
        for _ in range(self.num_blocks):
            assignment = [0] * self.num_blocks
            for i in range(self.num_blocks/2):
                assignment[i] = 1
            assignments.append(assignment)
        # return self.block_assignments
        return assignments
