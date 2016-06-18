#!/usr/bin/python2

import os
import re
import sys
import time
import socket
import errno

from sys import stdin, stdout
from struct import pack
from subprocess import check_output, CalledProcessError
from constants import *



# response for non exist content
HTTP404 = 'HTTP/1.1 404 Not Found\n'

# CDN domain name:
CDN_NAME = 'cs5700cdn.example.com'

# sys commands for clean up existing connection
FUSER_CMD = 'fuser {}/{}'
KILL_CMD = 'kill -9 {}'

# standard working directory: 
# go back here after writing to cache
WORK_DIR = os.path.abspath(os.getcwd())



# this is the front end HTTP server runs at cs5700cdnproject.ccs.neu.edu 
# it asks the DNS server runs at the same server for IP of best replica host to contact
def clean_up(port, proto):
    try:
        pids_str = check_output(FUSER_CMD.format(port, proto), shell=True)

    except CalledProcessError as exe_error:
        # no such process
        pass

    else:
        pids = map(int, re.split('\W+', pids_str.strip()))
        for pid in pids:
            kill_output = check_output(KILL_CMD.format(pid), shell=True)
            # need to wait here
            time.sleep(3)


# read a given file contains list of peer ips
# formatted as one ip per line
def read_all_peers(filename):
    with open(filename, 'r') as hosts:
        return map( (lambda str: str.strip()), hosts.readlines())


# set the filename for neighbor list based on ip addrs
def get_neighbor_list(ip):
    digits = ip.split('.')
    prefix = ''.join([ (digit + '.') for digit in digits])
    return prefix + 'nbrs'



# create a TCP socket
def tcp_sock():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except OSError as sock_error:
        print ('Create TCP socket failed.')
        print (sock_error.strerror)
        sys.exit(sock_error.errno)
    else:
        return sock



# connect a TCP socket
def tcp_connect(sock, server, port):
    try:
        sock.connect((server, port))

    except OSError as sock_conn_error:
        print ('Connect TCP socket failed.')
        print (sock_conn_error.strerror)
        return False

    except socket.error as sock_error:
        if sock_error.errno == errno.ECONNREFUSED:
            print ('Server at {} has exited.'.format(server))
        return False

    else:
        return True



# create a UDP socket
def udp_sock():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except OSError as sock_error:
        print ('Create UDP socket failed.')
        print (sock_error.strerror)
        sys.exit(sock_error.errno)
    else:
        return sock


# bind a UDP socket to port
def udp_bind(sock, port):
    my_ip = get_src_ip()
    try:
        sock.bind((my_ip, port))
    except OSError as sock_error:
        print ('Binding UDP socket at {}:{} failed.'.format(my_ip, port))
        print (sock_error.strerror)
        sys.exit(sock_error.errno)
    else:
        return sock



# close an established socket
def close_sock(sock):
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()



# send msg through udp from a udp socket
# for query dns server
def send_msg(snd_sock, str_msg, dst_addr, dst_port=PORT):
    try:
        snd_sock.sendto(str_msg, (dst_addr, dst_port))
    except OSError as sock_error:
        print ('Message {} did not got sent.'.format(str_msg))
        print (sock_error.strerror)
        pass
    else:
        print ('Sent message {} to {}.'.format(str_msg, dst_addr))


# recv msg resp through udp from a binded socket
# for query dns server
def recv_msg(rcv_sock):
    try:
        data, addr = rcv_sock.recvfrom(MAX_LEN)
    except OSError as sock_error:
        print ('Udp socket cannot receive.')
        print (sock_error.strerror)
    else:
        return data



# send msg through connected socket
def send_data(snd_sock, str_msg):
    while True:
        try:
            #snd_sock.sendall(str_msg.encode('utf-8'))
            snd_sock.sendall(str_msg)

        except OSError as sock_send_error:
            print ('Sending msg of {} failed: '.format(str_msg))
            print (sock_send_error.strerror)
            continue
        break


# recv one piece of data through connected socket
def recv_data(rcv_sock, buf_len):
    resp = None
    while True:
        try:
            resp, src = rcv_sock.recvfrom(buf_len)
        except OSError as sock_recv_error:
            print ('Socket recving failed: ')
            print (sock_recv_error.strerror)
            continue
        break
    return resp

# send a stream of data pieces
def send_full_data(data, chunk_len, snd_sock, buf_len):
    pass

# recv a stream of data pieces
def recv_full_data(rcv_sock, buf_len):
    data = ''
    while True:
        chunk = recv_data(rcv_sock, buf_len)
        if chunk:
            #data += chunk.decode('utf-8')
            data += chunk
        else:
            break
    return data


# parse GET request and return (host, file)
def parse_get(request):
    # store GET request items in a dictionary
    get = {} 
    for line in request.splitlines():
        attrs = re.split(':* ', line)
        if len(attrs) > 1:
            get[attrs[0]] = attrs[1]
        else:
            get[attrs[0]] = None

    return (get['Host'], get['GET'])


# retrieve response status code return -1 on error
def get_status_code(resp_str):
    if len(resp_str.splitlines()) <= 1:
        return -1
    else:
        status = (resp_str.splitlines())[0]
        #print(status)
    
    if len(status.split()) <= 1:
        return -1
    else:
        status_code = status.split()[1]
    return status_code


# convert a file (html page) to string
def file_to_str(filename):
    with open(filename, 'r') as file:
        data = file.read()
    return data



# fetch a webpage from remote origin server and store it to cache
def fetch_page(host, port, filename):
    cli_sock = tcp_sock()
    tcp_connect(cli_sock, host, port)
    msg = 'GET {} HTTP/1.1\nHost: {}\n\n'.format(filename, host)
    send_data(cli_sock, msg)
    print (msg)
    html = recv_full_data(cli_sock, MAX_LEN)

    if len(html) == 0:
        html = HTTP404
    close_sock(cli_sock)
    return html



# make multi-level directories
def mkdirs(dirs):
    curr_dir = '.'
    levels = dirs.split('/')
    print (levels)

    for i in range (0, len(levels)):
        # skip trivial dir
        if levels[i] == '':
            i += 1
            continue

        curr_level = './' + levels[i]
        #print (curr_level)

        if os.path.isdir(curr_level):
            os.chdir(curr_level)
        else:
            os.mkdir(curr_level)
            os.chdir(curr_level)
        #print (os.getcwd())



# write a file relatively to current directory
def write_file(full_path, html):
    filename = full_path.split('/').pop()
    filename_start = re.search(filename, full_path).start()

    dirs = full_path[:filename_start]
    # go through directories: 
    # skip if exists, mkdir if not 

    mkdirs(dirs)
    # print ('Directories created: ' + dirs)
    # print ('Currrent directory: ')
    # print (os.getcwd())

    with open(filename, 'w') as new_cache:
        new_cache.write(html)

    # return to work directory
    os.chdir(WORK_DIR)


# traverse a directory
def traverse_dir(dir):
    #print (dir)
    roots = []
    fileslist = []

    for root, dirs, files in os.walk(dir):
        roots.append(root)
        fileslist.append(files)

    level = 0
    total_size = 0
    cache_dict = {}
    for files in fileslist:
        if len(files) > 0:
            for file in files:
                full_path = os.path.join(roots[level], file)
                file_size = os.path.getsize(full_path)
                total_size += file_size
                cache_dict[full_path] = file_size 
        level += 1
    return [total_size, cache_dict]




# convert a string represented ip address
# into hex in byte string ready to send 
# '129.10.116.81' => b'\x81\x0a\x74\x51'
def ip_to_bytes(ip):
    result = b''
    ip_list = ip.split('.')
    for i in range(0, len(ip_list)):
        val = int(ip_list[i])
        # 'B': unsigned char
        result += pack('B', val)
    return result


# retrieve local ip addr from outside 
def get_src_ip():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
        except OSError as sock_error:
            continue
        break
    return s.getsockname()[0]




if __name__=='__main__':
    print ('Enter your query: ')
    query = stdin.readline()
    print ('You have entered: ' + query)

