#Project: Dual Server Video Streaming
#Group: ECE No.9 2012-2013
#Author: James Zhao, Yu-chung Chau, Varoon Wadhawa
#Date: June,2,2013
#Copyright (c) 2013 All Right Reserved

#Description: client code for udp dual case. Run on aspitrg1 after running udp server code on aspitrg3 and aspitrg4. 
#Currently configured to connect to aspitrg3 and aspitrg4. Uses asynchronous sockets to download from both servers with a specified delay.
#Generates two logs one for each socket connection containing time intervals for each downloaded chunk.
#How to run: python udpclient_dual.py 

import socket, fcntl, sys, datetime, struct, select

# Variables #
serverPort = 5005
clientPort1 = 5678
clientPort2 = 6000
eth0 = 'eth0'
eth1 = 'eth1'
fileName = 'fun.MOV'
bufferSize = 1024
s1write = 'sData1'
s2write = 'sData2'
log1 = 'rcvLog1.txt'
log2 = 'rcvLog2.txt'

#server IPs#
aspitrg3 = "129.25.57.233"
aspitrg4 = "129.25.57.234"

def parse_args():
        if len(sys.argv) != 3 :
                print 'usage: client.py <server1IP> <server2IP>'
                sys.exit()
        else:
                sIP1 = sys.argv[1]
                sIP2 = sys.argv[2]
                return sIP1, sIP2 
                
def test_args():
        sIP1 = aspitrg3
        sIP2 = aspitrg4
        return sIP1, sIP2

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

#Asynchornized selection function for dual server file transfer
def runSelect(recvList):
    selectUnsuccessful = True
    while selectUnsuccessful:
        try:
            # no timeout used in this select call. So, we will not catch inactive clients and
            # close them. Other than that, this code catches everything else.
            readyRecvList, readySendList, readyErrList = select.select( recvList, [], [] )
            selectUnsuccessful = False
        # if there is a select error, we have to figure out which socket caused this error.
        # if it is the listening socket, maybe we should exit the server program
        # altogether. If it is one of the connected sockets, then we should close that
        # socket and remove it from the list we use for the select() function and run
        # select() again.
        except select.error:
            for fd in recvList:
                try:
                    tempRecvList, tempSendList, tempErrList = select.select( [ fd ], [], [], 0 )
                except select.error:
                    if ( fd == myServerSocket ):
                        fd.close()
                        exit( 1 )
                    else:
                        if fd in recvList:
                            recvList.remove( fd )
                        fd.close()
    return readyRecvList

def handleConnectedSocket(sock, readyList, serverList, startTime):
        bytesRecvd1 = 0
        bytesRecvd2 = 0
        f1 = open(s1write, "wb")
        f2 = open(s2write, "wb")
        writelog1 = open(log1, 'w')
        writelog2 = open(log2, 'w')
        try:
                while True:    
                        #sock.settimeout(10)
                        chunks, server = sock.recvfrom( bufferSize )
                        print 'received {} bytes from {}'.format(len(chunks),server)
                        if sock == serverList[0]:
                                bytesRecvd1 += len(chunks)
                                #f1.write(chunks)
                                timeTaken = datetime.datetime.now()-startTime
                                writelog1.write(str(timeTaken.total_seconds()) + '\n')
                                #break
                        else if sock == serverList[1]:
                                bytesRecvd2 += len(chunks)
                                #f2.write(chunks)
                                timeTaken = datetime.datetime.now()-startTime
                                writelog2.write(str(timeTaken.total_seconds()) + '\n')
                                #break
        
        except socket.timeout:
                print "File Downloaded"
                if sock == serverList[0]:
                        f1.close()
                        writelog1.close()
                else:
                        f2.close()
                        writelog2.close()
                writelog.close()
        except socket.error as err:
                print "Something awful happened with a connected socket:", err
                # You should check if it is in the list, because it may have been removed due to
                # some other error, but may have caused a socket error before closing the socket.
                if sock in serverList:
                    readyList.remove( sock )
                sock.close()

def bindto(dev, cPort):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cIP = get_ip_address(dev)
        sock.setblocking(0)
        sock.bind((cIP,cPort))
        print 'client socket binded to {} on port {} '.format(cIP, cPort)
        return sock

def sendFileRequest(sock, fileName, sIP, sPort):
        bytesSent = sock.sendto(fileName, (sIP, sPort))
        print 'sending {} file request to server @ {} on port {} at {} '.format(fileName, sIP, sPort, datetime.datetime.now())

def main():
        serverIP1, serverIP2 = test_args()

        clientSock1 = bindto(eth0, clientPort1)
        clientSock2 = bindto(eth1, clientPort2)

        sendFileRequest(clientSock1, fileName, serverIP1, serverPort)
        sendFileRequest(clientSock2, fileName, serverIP2, serverPort)

        start = datetime.datetime.now()

        myRecvList = [ clientSock1, clientSock2 ]             

        try:
            while True:
                readyForRecv = runSelect(myRecvList)
                for fd in readyForRecv:
                        handleConnectedSocket(fd, readyForRecv, myRecvList, start)
        except KeyboardInterrupt:
                print "File Downloaded!"
                for fd in myRecvList:
                        fd.close()
                print "\nClosing all sockets and exiting. Goodbye!"
        
if __name__ == '__main__':
        main()
