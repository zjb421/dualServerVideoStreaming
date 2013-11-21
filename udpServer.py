#Project: Dual Server Video Streaming
#Group: ECE No.9 2012-2013
#Author: James Zhao, Yu-chung Chau, Varoon Wadhawa
#Date: June,2,2013
#Copyright (c) 2013 All Right Reserved

#Description:

import socket, fcntl, sys, datetime, struct, os, time

# Variables #
serverPort = 5005
clientPort = 5678
devName = 'eth0'
bufferSize = 1024
delay = 0.01

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def bindto(dev, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sIP = get_ip_address(dev)
    sock.bind((sIP,port))
    print 'server socket binded to {} on port {} '.format(sIP, port)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return sock

def getFileRequest(sock):
    try:
        fileRequest, client = sock.recvfrom(bufferSize)
        print 'received {} bytes from {}'.format(len(fileRequest),client)
        print 'file requested is: ' + fileRequest

        if not os.path.exists(fileRequest):
            print 'Error: No such file: %s' % fileRequest
            sys.exit()

        else:
            return fileRequest, client

    except socket.error:
        sock.close()
        sys.exit()

def sendFile(sock, fileName, cAddr): #udp
    inputf = open(fileName)
    while True:
        byteSize = inputf.read(bufferSize)
        if not byteSize: # no more data to read
            inputf.close()
            return

        try:
            sock.sendto(byteSize, cAddr) #blocking call?
            time.sleep(delay)
        except socket.error:
            print 'socket error encountered'
            sock.close()
            sys.exit()

def main():
    try:
        serverSock = bindto(devName,serverPort)
        fileRequested, clientAddress = getFileRequest(serverSock)
        sendFile(serverSock, fileRequested, clientAddress)

    except KeyboardInterrupt:
        print "\nClosing connection and exiting because of keyboard interrupt. Goodbye!"
        serverSock.close()

    finally:
        serverSock.close()

if __name__ == '__main__':
    main()
