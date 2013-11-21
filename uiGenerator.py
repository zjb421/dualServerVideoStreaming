#Project: Dual Server Video Streaming
#Group: ECE No.9 2012-2013
#Author: James Zhao, Yu-chung Chau, Varoon Wadhawa
#Date: June,2,2013
#Copyright (c) 2013 All Right Reserved

#Description: ui code for generating dynamic graph from logs placed onto the website html file. 
#How to run: python ui_generator.py 

import matplotlib.pyplot as plt
import numpy
import sys
import urllib.request
import time

from multiprocessing import Process


def plot_graph(title,log,pic):
    print("Running...")
    
    lines=[]
    max_points=150;
            
    while True:
        f = open(log)
        newLines = f.readlines()
        f.close()
        
        if (newLines != lines):
            lines=newLines
            plt.clf()        
            x_data=[]
            y_data=[]
            if (len(lines) <= max_points):
                for x in range(0,len(lines)):
                    coordinates=lines[x].split(' ')
                    if (len(coordinates) > 1):
                        if (coordinates[1] != "[]"):
                            coordinates[1]=coordinates[1].replace('\n','').replace('[','').replace('\'','').replace(']','')
                            x_data.append(coordinates[0])
                            y_data.append(coordinates[1])
                    #time.sleep(1)
            else:
                for x in range(len(lines)-max_points,len(lines)):
                    coordinates=lines[x].split(' ')
                    if (len(coordinates) > 1):
                        if (coordinates[1] != "[]"):
                            coordinates[1]=coordinates[1].replace('\n','').replace('[','').replace('\'','').replace(']','')
                            x_data.append(coordinates[0])
                            y_data.append(coordinates[1])
                    #time.sleep(1)
        
            fig=plt.figure()
            ax=fig.add_subplot(111)
            ax.set_axis_bgcolor("#fdf8ca")
            ax.set_xlabel('Time')
            ax.set_ylabel('Throughput')
            ax.set_title(title)
            ax.plot(x_data,y_data)
            ax.grid(color='k', linestyle='-', linewidth=.1)
            fig.savefig(pic)
        #
            ip_coordinates=[]
            ip=[]
            f=open("ip.txt")
            ip_input=f.read()
            f.close()
            ip=ip_input.split(',')
            ip[0]=ip[0].replace('(','').replace('\'','')
        
            with urllib.request.urlopen('http://api.hostip.info/get_html.php?ip='+ip[0]+'&position=true') as url:
                response=url.readlines()
            response[3]=response[3].decode("utf-8").replace("Latitude: ",'').replace('\n','')
            response[4]=response[4].decode("utf-8").replace("Longitude: ",'').replace('\n','')
            ip_coordinates.append(response[3])
            ip_coordinates.append(response[4])
            f = open("interface_template.txt")
            template_data = f.read()
            f.close()
            template_data=template_data.replace("long_val",ip_coordinates[1]).replace("lat_val",ip_coordinates[0])
            f = open("index.html",'w')
            f.write(template_data)
            f.close()



f = open("interface_template.txt")
template_data = f.read()
f.close()
f = open("index.html",'w')
f.write(template_data)
f.close()

plot_graph('Single Server Throughput(chuncks/sec vs. time)','throughput_cowgirl.txt','p1.png')
plot_graph('Single Server Throughput(chunks/sec vs. time)','data1.txt','p1.png')
plot_graph('Dual Server Throughput(chuncks/sec vs. time)-combined','throughput_fun.txt','p2.png')
plot_graph('Dual Server Throughput(chunks/sec vs. time)-combined','data2.txt','p2.png')
p1= Process(target=plot_graph, args =('Single Server Throughput(chuncks/sec vs. time)','data1.txt','p1.png'))
p1.start()
p2= Process(target=plot_graph, args = ('Dual Server Throughput(chuncks/sec vs. time)-combined','data2.txt','p2.png'))
p2.start()
