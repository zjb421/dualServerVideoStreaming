//Project: Dual Server Video Streaming
//Group: ECE No.9 2012-2013
//Author: James Zhao, Yu-chung Chau, Varoon Wadhawa
//Date: June,2,2013
//Copyright (c) 2013 All Right Reserved

//Description: ActionScipt is the play and pause script that controls the automatic manufactored buffer starvation. That use the log files from the servers transfering

//on the frame
timeStamp = import("timeStamp.txt");
eachStmp = timeStamp.split(" ");
stamp = eachStmp[0];

stop();
function myfunction() {
	clearInterval(myInterval);
	play();
}

myInterval = setInterval(myfunction, stamp);