#Project: Dual Server Video Streaming
#Group: ECE No.9 2012-2013
#Author: James Zhao, Yu-chung Chau, Varoon Wadhawa
#Date: June,2,2013
#Copyright (c) 2013 All Right Reserved

#Description: client code for tcp single case. Run on aspitrg1 after running tcp server code on aspitrg3 or aspitrg4. 
#Download movie from specified server and generates one log of timestamp for each chunk. 
#How to run: python tcpclientsingle.py <serverIPaddress>

## TCP Client Implementation ##
import socket,fcntl, sys, datetime, struct, os, time

# Variables #
serverPort = 5005
clientPort = 5678
bufferSize = 65535	
fileSize = 8606106
log = 'singleLog.txt'
writebackFile = 'A.Walk.In.The.Clouds.1995.720p.BluRay.x264-CiNEFiLE.mkv'

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

def connect_to(server_ip, server_port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.connect((server_ip, server_port))
	print 'client connected to {} on port {} '.format(server_ip, server_port)
	return sock
	
def get_file(sock,startTime):
	bytesRecvd = 0
	writelog = open(log, 'wb')
	while True:
		rec = sock.recv(bufferSize)
		bytesRecvd += len(rec)
		print 'received {} bytes from {}'.format(len(rec),sock.getpeername())
		if not rec:
			break
		timeTaken = datetime.datetime.now()-startTime
		writelog.write(str(timeTaken.total_seconds()) + '\n')
	writelog.close()
	print 'Transmission Completed'
	return bytesRecvd


	
def main():
        parse_args()
        serverIP = sys.argv[1]
        try:
				connectedSock = connect_to(serverIP,serverPort)
				start = datetime.datetime.now()
				downloadSize = get_file(connectedSock, start)
				elapsed = datetime.datetime.now() - start
				print 'Got %d bytes in %s seconds' % (downloadSize, elapsed)
        except KeyboardInterrupt:
                print "\nClosing connection and exiting because of keyboard interrupt. Goodbye!"
                connectedSock.close()
        finally:
                connectedSock.close()

if __name__ == '__main__':
    main()
