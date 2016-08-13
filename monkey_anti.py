__author__ = 'oleh'

import time

l = []


def foo(param):
    l.append(param)


t_start = time.time()

i = 0
while time.time() - t_start < 1:
    l.append(i)
    # i += 1
    # print time.time() - t_start

print "It came to an end at index=%d" % l.__sizeof__()