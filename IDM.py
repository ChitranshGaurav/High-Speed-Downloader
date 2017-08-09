"""
* Author : Chitransh Gaurav
* Title : IDM Multithreaded Downloader
* System Requirements : Python 2.7.6 on Linux
"""
import os
import threading
import sys
import time
import urllib2

#Enter the url here:

weburl = raw_input("Enter the url: ")

threadcnt = input("Enter no. of threads: ")# ideally 50-150 No. of threads as per requirement

#intitializing global variables
connection = False
pusave=0.0
pudwnld=0.0
count = 0
flag = True
speed = 0.0
maxspeed = 0
downloaded = 0.0
unit = " KB"
div = 1024.0
stopped_threads = 0
current_threads = 0
lock = threading.Lock()

def newDir():
	dirname = "IDMtemp"	
	cnt = 0
	while(os.path.exists(dirname+str(cnt))):
		cnt += 1
	return dirname+str(cnt)

def odometer():
	global pusave, pudwnld, speed, maxspeed, flag
	while flag:
		time.sleep(1)
		with lock:
			tempvar = time.time()
			speed = (pudwnld)/(tempvar - pusave)
			maxspeed = max(maxspeed,speed)
			pudwnld = 0.0
			pusave = tempvar

def display():
	spdunit = "KB"
	global lock, count, filesize, downloaded, unit, div, speed, current_threads
	filesize_tmp = downloaded/div
	spd = speed/1024
	if(spd >= 1024):
		spd /= 1024.0
		spdunit = "MB"
	remaining_time = 1000000
	if(speed > 0):
		remaining_time = int((filesize-downloaded)/speed)
	percentage = (downloaded/filesize)*100
	if(filesize_tmp >= 1024):
		filesize_tmp /= 1024.0
		div *= 1024.0
		if(unit == " KB"):
			unit = " MB"
		elif(unit == " MB"):
			unit = " GB"
	print("Downloaded : %0.4f %s"%(filesize_tmp,unit))
	print("Download Speed : %0.2f %s/second"%(spd, spdunit))
	print("Finished : %0.2f %%"%(percentage))
	if(speed > 0):
		print("ETA : %d minutes %d sec"%(remaining_time/60 , remaining_time % 60))
	else:
		print("Waiting")
	T = 0
	for T in range(4):
		sys.stdout.write("\033[F")

def IDM_main(url,start,end,filename, block_size = 8192):
	global speed, downloaded, lock, pusave, pudwnld, filesize, current_threads, count, stopped_threads
	#spoofing request header as some servers may
	#not allow script generated requests
	sphdr = {'User-Agent' : 'Mozilla/5.0'}#Firefox/2.0.0.11
	reqobj = urllib2.Request(weburl, headers = sphdr)
	reqobj.add_header('Range', 'bytes=' + str(start) + '-' + str(end))
	connection = False
	fp = open(filename, 'wb')
	stopped_threads += 1
	while(connection == False):
		try:
			response = urllib2.urlopen(reqobj,timeout = 6)
			metainfo = response.info()
			if(len(metainfo.getheaders('Content-Length')) > 0):
				connection = True
				if(metainfo.getheaders('Content-Length')[0] == filesize and start != 0):
					count -= 1
					return
		except:
			time.sleep(3)
			connection = False
	dwnld = 0
	current_threads += 1
	stopped_threads -= 1
	while True:
		try:
			buffer = response.read(block_size)
		except:
			current_threads -= 1
			stopped_threads += 1
			reqobj = urllib2.Request(weburl, headers = sphdr)
			reqobj.add_header('Range', 'bytes=' + str(start+dwnld) + '-' + str(end))
			connection = False
			while(connection == False):
				try:
					response = urllib2.urlopen(reqobj, timeout = 5)
					metainfo = html.info()
					if(len(metainfo.getheaders('Content-Length')) > 0):
						connection = True
				except:
					time.sleep(3)
					connection = False
			current_threads += 1
			stopped_threads -= 1
			continue

		if not buffer:
			break
		pudwnld += (len(buffer))
		dwnld += (len(buffer))
		downloaded += (len(buffer))

		fp.write(buffer)
		with lock:
			display()
	current_threads -= 1
	count -= 1

tokens = weburl.split('/')
filename = tokens[len(tokens)-1] #Name of the file
if(len(filename) > 128):
	filename = "IDMfile"
	cnt = 0
	while(os.path.exists(filename + str(cnt))):
		cnt += 1
	filename = filename + str(cnt)


spoofhdr = {'User-Agent' : 'Mozilla/5.0'}
reqobj = urllib2.Request(weburl, headers = spoofhdr)

while(connection == False):
		html = urllib2.urlopen(reqobj)#default timeout
		metainfo = html.info()
		if(len(metainfo.getheaders('Content-length')) > 0):
			connection = True
		else:
			time.sleep(5)
filesize = int(metainfo.getheaders('Content-Length')[0])
tempvar = filesize/1024.0
if(tempvar >= 1024):
	tempvar /= 1024
	if(tempvar >= 1024):
		tempvar /= 1024
		units = "GB"
	else:
		units = "MB"
else:
	units = "KB"

print("File Name : " + urllib2.unquote(filename))
print("File Size : %0.4f"%(tempvar) + units + "\n")
folder = newDir()
os.makedirs(folder)

load = max(102400, filesize/threadcnt)

start = 0
files = []
starttime = time.time()
threadit = threading.Thread(target = odometer)
threadit.start()
iteri = 0
while(start <= filesize):
	name = folder+"/temp"+str(iteri)
	threadit = threading.Thread(target = IDM_main, args = (weburl, start, min(filesize-1, start+load), name))
	files.append(name)
	start += (load+1)
	threadit.start()
	count += 1
	iteri += 1

while(count):
	time.sleep(2)

flag = False
time_elapsed = time.time() - starttime
print("Total Time Consumed : %d minutes : %d secs"%(time_elapsed/60, time_elapsed%60))
print("Average Speed : %0.4f KB/s"%(filesize/(1024.0*time_elapsed)))
print("Maxspeed : %0.4f KB/s"%(maxspeed/(1024*1024.0)))
filename = urllib2.unquote(filename)
if(os.path.exists(filename)):
	cnt=0
	while(os.path.exists(filename)):
		filename=str(cnt)+filename
with open(filename, 'w') as outfile:
	for fileit in files:
		with open(fileit) as infile:
			for line in infile:
				outfile.write(line)
		os.remove(fileit)
os.rmdir(folder)
	
print("Download Finished")
