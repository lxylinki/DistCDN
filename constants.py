#!/usr/bin/python2

# Assume the total number of replica servers
# is static, hosts file contains their IP addresses
HOSTS = './hosts'

# The access port of this CDN for HTTP server and DNS server
# Server ports can be overwritten from command line when invoking
PORT = 65533

# socket buffer size
MAX_LEN = 4096

# Cache update/delete message ports
UPDATE_PORT = PORT+1
DEL_PORT = PORT-1

# Informal DNS lookup from HTTP to local DNS server
INNER_QUERY_PORT = PORT-2

# The cache directory
CACHE_DIR = './cache/'
# Max bytes of cache
CACHE_LIMIT = 8000000

# This is the IP address of the original server
# served by this CDN
ORIGIN_IP = '54.88.98.7'
ORIGIN_PORT = 8080
ORIGIN = 'ec2-54-88-98-7.compute-1.amazonaws.com'

# Assigned CDN domain name
# names other than this could also be accepted
CDN_NAME = 'cs5700cdn.example.com'

# The signal command to exit DNS and HTTP servers
EXIT_CMD = 'exit'

