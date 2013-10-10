"""
Configuration class.

Holds information about the current configuration and is able to pass the data to- or from disk.
"""


class Config:
    def __init__(self):
        self.apn = "internet.telenor.se"
        self.server = "127.0.0.1"
        self.root = ""
        self.port = 80
        self.uid = ""
