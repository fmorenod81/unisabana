#!/usr/bin/python


#This is a "module" script, by which I mean that appsitefunctions.loadbasehtml() uses this to create a section of the site.

# Turn on debug mode.
import cgitb
import os
cgitb.enable()
import appsitefunctions
import time

#This section will grab the name of the app server host name from the mtwa.conf file
dbServerHostname=os.getenv("DBSERVER_RO")

# Connect to the database.
import pymysql
try:
	conn = pymysql.connect(
	    db='appdemo',
	    user='appdemo',
	    passwd='appdemo1',
	    host=dbServerHostname)
        c= conn.cursor()
        start_time = time.time()
				
	#Grab the table data from the database.
	c.execute("SELECT * FROM demodata")
        #Take final time and its difference
	end_time = time.time()
	exec_time =  end_time - start_time


	#Start HTML print out, headers are printed so the Apache server on APP does not produce a malformed header 500 server error
	print '''
	<Content-type: text/html\\n\\n>
	<html>
	<head>
	<title>Multi-Tier Web App</title>
	</head>
	<body>
	<table border="1">
	'''

	#Start printing the html for the header row
	print '<center><h3>View Data on {}</h3></center>'.format(dbServerHostname)
        print '<center><b>Query: {1} results on {0} secs </b></center>'.format(exec_time, c.rowcount)
	print '<table style="width:100%" border="1">'
	print '<tr>'
	print '<td><b>ID</b></td>'
	print '<td><b>Name</b></td>'
	print '<td><b>Notes</b></td>'
	print '<td><b>Timestamp</b></td>'
	print '</tr>'

	#now to print within the table with the contents of the database
	for each in c.fetchall():
		print '<tr>'
	 	print '<td>',each[0], '</td>'
	 	print '<td>',each[1], '</td>'
	 	print '<td>',each[2], '</td>'
	 	print '<td>',each[3], '</td>'
	 	print '</tr>'

	print '</table>'
	print '</center>'

	#Finish printing headers 
	print '''
	</table>
	</body>
	</html>
	'''
except:
	
	appsitefunctions.printdbservererror()


