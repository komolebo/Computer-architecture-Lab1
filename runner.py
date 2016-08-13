import subprocess
import configparser
import sys


config = configparser.ConfigParser()
config.read('../conf.INI')

path_items = config.items("paths")


print "file running from path ", path_items[0][1]
subprocess.call([sys.executable, path_items[0][1]])