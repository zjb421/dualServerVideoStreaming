#Project: Dual Server Video Streaming
#Group: ECE No.9 2012-2013
#Author: James Zhao, Yu-chung Chau, Varoon Wadhawa
#Date: June,2,2013
#Copyright (c) 2013 All Right Reserved

#Description:

## TCP Server Implementation ##

import socket,fcntl, sys, datetime, struct, os, time

# Variables #
deviceName = 'eth0'
serverPort = 5005
bufferSize = 1024
fileServing = 'A.Walk.In.The.Clouds.1995.720p.BluRay.x264-CiNEFiLE.mkv'
delay = 0.1

def get_ip_address(ifname):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	return socket.inet_ntoa(fcntl.ioctl(
		s.fileno(),
		0x8915,  # SIOCGIFADDR
		struct.pack('256s', ifname[:15])
	)[20:24])

def bind_to(device_name, server_port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_ip = get_ip_address(device_name)
	sock.bind((server_ip,server_port))
	print 'server socket binded to {} on port {} '.format(server_ip,server_port)
	return sock
	
def serve(listen_socket, file_name):
	if not os.path.exists(file_name):
		print 'Error: No such file: %s' % file_name
		sys.exit()
	else:	
		connected_socket, address = listen_socket.accept()
		print 'Somebody at {} wants to watch movies!'.format(address)
		send_file(connected_socket, file_name)
		
def send_file(connected_sock, file_name):
	"""Send chunks of file down the socket."""
		
	inputf = open(file_name)

	while True:
		byte_data = inputf.read(bufferSize)

		if not byte_data: # no more movies 
			connected_sock.close()
			inputf.close()
			return


		try:
			connected_sock.sendall(byte_data) # this is a blocking call
		except socket.error:
			connected_sock.close()
			inputf.close()
			return
	
def main():
	try:
		listenSock = bind_to(deviceName,serverPort)
		print 'Listening for connections...'
		listenSock.listen(1)
		
		serve(listenSock, fileServing)
		print '\nFile transmission completed!' 
	except KeyboardInterrupt:
		print "\nClosing connection and exiting because of keyboard interrupt. Goodbye!"
		listenSock.close()

if __name__ == '__main__':
	main()
