#!/usr/bin/python
import string, random
import socket
import time

print '''
Random data generator
'''

time.sleep(15)

def random_generator(size=6291456, chars=string.printable):
 return ''.join(random.choice(chars) for _ in range(size))

print socket.gethostname() + '  ' + random_generator() + '  ' + socket.gethostname()
