import os

def makedirp(path):
    if not os.path.exists(path):
        os.makedirs(path)
