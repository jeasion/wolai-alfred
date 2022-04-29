import json


class Payload(object):
    def __init__(self, j):
        self.data = None
        self.recordMap = None
        self.results = None
        self.__dict__ = json.loads(j)
