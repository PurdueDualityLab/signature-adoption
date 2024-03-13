'''
stage.py: This module contains the abstract parent class for all stages.
'''
from abc import ABC, abstractmethod


class Stage(ABC):
    '''
    This class is the parent class for all stages.
    '''

    def __init__(self, args):
        self.args = args

    @abstractmethod
    def huggingface(self):
        pass

    @abstractmethod
    def docker(self):
        pass

    @abstractmethod
    def maven(self):
        pass

    @abstractmethod
    def pypi(self):
        pass

    @abstractmethod
    def run(self):
        pass
