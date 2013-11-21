#Project: Dual Server Video Streaming
#Group: ECE No.9 2012-2013
#Author: James Zhao, Yu-chung Chau, Varoon Wadhawa
#Date: June,2,2013
#Copyright (c) 2013 All Right Reserved

#Description: client code udp single case. Run on aspitrg1 after running udp server code on aspitrg3 or aspitrg4. 
#Request and downloads the specified movie. Generates a specified log file containing timestamps and size of chunks received
#How to run: python udpclient_single.py <serverIPaddress>


import socket, fcntl, sys, datetime, struct

# Variables #
serverPort = 5005
clientPort = 5678
devName = 'eth0'
fileName = 'A.Walk.In.The.Clouds.1995.720p.BluRay.x264-CiNEFiLE.mkv'
bufferSize = 65535
fileSize = 8606106
log = 'single_UDP_recvLog.txt'

def parse_args():
        if len(sys.argv) != 2 :
                print 'usage: client.py <serverIP>'
                sys.exit()

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def bindto(dev, cPort):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cIP = get_ip_address(dev)
        sock.bind((cIP,cPort))
        print 'client socket binded to {} on port {} '.format(cIP, cPort)
        return sock

def sendFileRequest(sock, fileName, sIP, sPort):
        bytesSent = sock.sendto(fileName, (sIP, sPort))
        print 'sending {} file request to server @ {} on port {} at {} '.format(fileName, sIP, sPort, datetime.datetime.now())

def getFile(sock, fileName, startTime):
        bytesRecvd = 0
        writelog = open(log, 'w')
        try:
                while True:
                        sock.settimeout(10)
                        chunks, server = sock.recvfrom(bufferSize)
                        bytesRecvd += len(chunks)
                        timeTaken = datetime.datetime.now()-startTime
                        writelog.write(str(timeTaken.total_seconds()) + '\t' + str(len(chunks)) + '\n')
        except socket.timeout:
                writelog.close()
        return bytesRecvd

def main():
        parse_args()
        serverIP = sys.argv[1]
        try:
                clientSock = bindto(devName,clientPort)
                sendFileRequest(clientSock, fileName, serverIP, serverPort)
                start = datetime.datetime.now()
                downloadSize = getFile(clientSock, fileName,start)
                elapsed = datetime.datetime.now() - start
                                       
                print 'Got %d bytes in %s seconds' % (downloadSize, elapsed)

        except KeyboardInterrupt:
                print "\nClosing connection and exiting because of keyboard interrupt. Goodbye!"
                clientSock.close()

if __name__ == '__main__':
    main()
