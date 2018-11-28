from __future__ import absolute_import
from six.moves import range
from automation import CommandSequence, TaskManager
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
    def __init__(self, num_browsers, data_directory="~/Desktop/", stages=[]):
        self.num_browsers = num_browsers
        self.stages = stages
        self.data_directory = data_directory
        self.manager = self.init_manager()

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
    
    def run(self):
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
