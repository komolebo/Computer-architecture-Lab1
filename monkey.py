__author__ = 'oleh'

import gevent
import time

l = []


def foo():
    i = 1000000
    while i > 0:
        l.append(1)
        i -= 1
        print "1"


def bar():
    i = 1000000
    while i > 0:
        l.append(0)
        i -= 1
        print "2"


t_start = time.time()

wrk = [gevent.spawn(foo), gevent.spawn(bar)]
gevent.joinall(wrk)

t_end = time.time()

# print l
print t_end - t_start
