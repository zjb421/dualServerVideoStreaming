#Project: Dual Server Video Streaming
#Group: ECE No.9 2012-2013
#Author: James Zhao, Yu-chung Chau, Varoon Wadhawa

#Description: client code for tcp dual case. Run on aspitrg1 and currently configured to connect to aspitrg3 and aspitrg4.
#Uses asynchronous sockets to request and download movie from both servers. Run after running server code on aspitrg3 and aspitrg4.
#Generates two logs one for each socket of the timestamps and number of accumulated bytes.
#How to run: python tcpclientdual.py 

## TCP Client Implementation ##

import socket,fcntl, sys, datetime, struct, os, time, select, errno

# Variables #
serverPort = 5005
clientPort1 = 5678
clientPort2 = 6000
bufferSize = 1024
fileSize = 8606106
log1 = 'receiveLog1.txt'
log2 = 'receiveLog2.txt'

# server ips #
aspitrg2 = '129.25.57.232'
aspitrg3 = '129.25.57.233'
aspitrg4 = '129.25.57.234'

def parse_args():
	if len(sys.argv) != 3:
		print 'usage: client.py <server1ip> <server2ip>'
		sys.exit()
	else:
		server1_ip = sys.argv[1]
		server2_ip = sys.argv[2]
		return server1_ip, server2_ip

def test_args():
	server1_ip = aspitrg3
	server2_ip = aspitrg4
	return server1_ip, server2_ip

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
	s.fileno(),
	0x8915,  # SIOCGIFADDR
	struct.pack('256s', ifname[:15])
    )[20:24])
	
def format_address(address):
    host, port = address
    return '%s:%s' % (host or '127.0.0.1', port)
	
def get_file(sockets, start_time):
	"""Download file from all the given sockets."""
	byteData = dict.fromkeys(sockets, '') # socket -> accumulated poem
    # socket -> task numbers
	sock2task = dict([(s, i + 1) for i, s in enumerate(sockets)])
	sockets = list(sockets) # make a copy
    # we go around this loop until we've gotten all the poetry
    # from all the sockets. This is the 'reactor loop'.
	writelog1 = open(log1, 'w')
	writelog2 = open(log2, 'w')
	
	while sockets:
		# this select call blocks until one or more of the
		# sockets is ready for read I/O
		rlist, _, _ = select.select(sockets, [], [])
		# rlist is the list of sockets with data ready to read
		for sock in rlist:
			data = ''
			while True:
				try:
					new_data = sock.recv(1024)
				except socket.error, e:
					if e.args[0] == errno.EWOULDBLOCK:
					# this error code means we would have
					# blocked if the socket was blocking.
					# instead we skip to the next socket
						break
					raise
				else:
					if not new_data:
						break
					else:
						data += new_data
						timeTaken = datetime.datetime.now()-start_time
			# Each execution of this inner loop corresponds to
			# working on one asynchronous task in Figure 3 here:
			# http://krondo.com/?p=1209#figure3
			task_num = sock2task[sock]

			if not data:
				sockets.remove(sock)
				sock.close()
				print 'Task %d finished' % task_num
				if task_num == 1:
					writelog1.close()
				else:
					writelog2.close()
			else:
				addr_fmt = format_address(sock.getpeername())
				msg = 'Task %d: got %d bytes of video from %s'
				#print  msg % (task_num, len(data), addr_fmt)
				if task_num == 1:
					writelog1.write(str(timeTaken.total_seconds()) + '\t' + str(len(data)) + '\n')
				else:
					writelog2.write(str(timeTaken.total_seconds()) + '\t' + str(len(data)) + '\n')	
			byteData[sock] += data
	return byteData 
	
def connect_to(address):
   """Connect to the given server and return a non-blocking socket."""
   
   sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   sock.connect(address)
   sock.setblocking(0)
   sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
   print 'client connected to {} '.format(address)
   return sock
	
def main():
	#parse_args()
	addresses = ((aspitrg3, 5005), (aspitrg4, 5005))
	start = datetime.datetime.now()
	sockets = map(connect_to,addresses)
	dataReceived = get_file(sockets,start)
	elapsed = datetime.datetime.now() - start
	for i, sock in enumerate(sockets):
		print 'Task %d: %d bytes of video' % (i + 1, len(dataReceived[sock]))
	print 'Got %d video in %s' % (len(addresses), elapsed)

if __name__ == '__main__':
    main()
