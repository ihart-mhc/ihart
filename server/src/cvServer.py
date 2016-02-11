"""
The iHart server uses the library openCV to detect motion and faces in a video feed.
It then edits the data, combining the motion ares to make them more representative of
the actual motion (without this, motion causes many small blobs around the edges), and
testing the found items for presence within areas of interest. The program the sends an
encoded string to give the coordinates of the blobs within each area of interest, using
using sockets, to communicate with client programs which decode the data and push events
at listening programs.

Part of the intention behind the project is to allow relatively inexperienced programmers
to create interactive programs that utilize computer vision.


When starting the program, a prompt appears with the option to choose a camera index.
Unless the computer has access to multiple cameras (and you wish to use one of them),
choose 0. Then drag the start trackbar to 1, starting the rest of the program. Three
windows will appear: if not all are visible, drag the top one(s) out of the way.

To draw an area of interest, click on the video feed window and drag: if unsatisfied with
the starting location, simply make it smaller until it turns red and release the mouse; it
will not be saved. Edit settings through thr trackbar window. To reset areas of interest,
simply change the position of the trackbar.

@author Kim Faughnan, 2013
		Drawing on work done by Cleo Schneider and Audrey St. John.
"""


import socket	# the only module needed for all our socket interactions
import sys		# so that can exit()
import cv2		# openCV
import numpy	# needed for openCV
import math		# for utility functions


class SocketHandler():

	"""
	Manages a non-blocking server socket: searches for incoming connections (checkIncomingConnections)
	and sends messages to all found connections (sendInformation).
	"""

	server = None
	clients = []
	message = None
	host = None
	port = 0

	def __init__(self, host='', port=5204):
		"""
		Creates a server socket with the specified host and port number.
		Sets the socket to non-blocking, and sets it to listen for connections.
		@param host: The host address. Default value: ''
					 (gives the socket local address)
		@param port: The port number. Default value: 5204
					 (the port number of the majority of python applications)
		@return: none
		"""

		self.port = port
		self.host = host
		# Create the socket.
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try:
			# Attempt to bind the socket to the host and port
			# (Until this is done, one cannot do anything with the socket.)
			self.server.bind((self.host, self.port))
		except socket.error, message:
			# If the binding failed, exit.
			# (If the binding fails,  don't panic--if you run the code and it fails,
			# it is quite possible that if you wait a few moments and run it again,
			# it will work. A failure does not necessarily mean that something is
			# wrong with the host and the port number.)
			sys.exit()

		# Sets the server to non blocking. The server needs to check for connections
		# frequently so that all incoming requests are found, but it is quite possible
		# that there will be no requests; in this instance, we want to continue executing
		# instead of waiting for a connection (this is the default setting).
		#
		# Set the socket to listen for up to 10 incoming connections.
		self.server.setblocking(0)
		self.server.listen(10)

	def checkIncomingConnections(self):
		"""
		Accepts a waiting socket connection and add it to the list of clients
		to send information to. If there is no waiting connection, do nothing.
		(This is a non-blocking call.)
		@return: none
		"""

		try:
			# Accept any waiting socket connections and add them to the client list.
			client, address = self.server.accept()
			if client is not None:
				self.clients.append(client)
		except socket.error, error:
			# If there were no waiting connections, do nothing.
			return

	def sendInformation(self, message):
		"""
		Sends the specified message to every socket connection (every item of self.clients).
		If a connection has exited, catch the error and remove it from the list.
		@param message: The message to send to each waiting client.
		@return: none
		"""

		toRemove = []
		# Send the message to each client; add each exited client to toRemove.
		for client in self.clients:
			try:
				client.sendall(message)
			except socket.error:
				# A socket.error will be thrown when we try to send a message to
				# a socket connection that has exited. Add the connection to
				# our list to remove after we're done iterating through the
				# list of clients.
				toRemove.append(client)

		# Remove each item in toRemove from self.clients
		for remove in toRemove:
			self.clients.remove(remove)


class AreaOfInterest:
	"""
	Stores the starting (leftX, topY) and ending (rightX, bottomY) coordinates
	of an area of interest.
	"""
	leftX = 0
	rightX = 0
	topY = 0
	bottomY = 0

	def __init__(self, leftX, rightX, topY, bottomY):
		"""
		Initialize all instance fields.
		@param leftX: the starting x value, the lowest
		@param rightX: the ending x value, the highest
		@param topY: the starting y value, the lowest
		@param bottomY: the ending y value, the highest
		@return: none
		"""
		self.leftX = leftX
		self.rightX = rightX
		self.topY = topY
		self.bottomY = bottomY

	def __iter__(self):
		"""
		Defined so that AreaOfInterest can be added to a list.
		object.__iter__ is called when one needs to iterate over an object.
		@return: self
		"""
		return self

	def next(self):
		"""
		Defined so that AreaOfInterest can be added to a list.
		Since AreaOfInterest does not contain data to be iterated over within itself,
		stops iteration immediately by raising StopIteration.
		@return: none
		"""
		# This is the way to signal to an iterator that it should stop iterating;
		# it has reached the end.
		raise StopIteration

	def getWidth(self):
		"""
		Returns the width of the AreOfInterest
		@return: the width of the AreaOfInterest
		"""

		return self.rightX - self.leftX

	def getHeight(self):
		"""
		Returns the height of the AreOfInterest
		@return: the height of the AreaOfInterest
		"""

		return self.bottomY - self.topY


class Blob:
	"""
	Stores the starting (leftX, topY) and ending (rightX, bottomY) coordinates of
	either an area of motion, or a face. Performs slight analysis of the coordinates
	by checking for overlap with another (given) Blob, and by scaling the coordinates
	for a given set of dimensions when also given the current width and height.
	"""
	leftX = 0
	topY = 0
	width = 0
	height = 0
	rightX = 0
	bottomY = 0

	def __init__(self, leftX, rightX, topY, bottomY, width, height):
		"""
		Initializes all instance fields of Blob. Requires leftX and topY, and either
		rightX and bottomY or width and height (will fill in the two excluded fields
		using the given four). To exclude a field, pass in -1 or None. next is expected
		to be None.

		@param leftX: the starting x of the blob.
		@param rightX: the ending x of the blob.
					   (can be substituted with both width and height)
					   (to exclude, pass in -1)
		@param topY: the starting y of the blob.
		@param bottomY: the ending y of the blob.
						(can be substituted with both width and height)
						(to exclude, pass in -1)
		@param width: the width of the blob.
					  (can be substituted with rightX and bottomY)
					  (to exclude, pass in -1)
		@param height: the height of the blob.
					   (can be substituted with rightX and bottomY)
					   (to exclude, pass in -1)
		@return: none
		"""
		self.leftX = leftX
		self.topY = topY
		self.rightX = rightX
		self.bottomY = bottomY
		self.width = width
		self.height = height

		# fill in any empty fields
		if(rightX < 0 or bottomY < 0):
			self.updateEndingBoundaries()
		elif(width < 0 or height < 0):
			self.updateWH()

	def __iter__(self):
		"""
		Defined so that Blob can be added to a list.
		object.__iter__ is called when one needs to iterate over an object.
		@return: self
		"""
		return self

	def next(self):
		"""
		Defined so that Blob can be added to a list.
		Since Blob does not contain data to be iterated over within itself,
		stops iteration immediately by raising StopIteration.
		@return: none
		"""
		# This is the way to signal to an iterator that it should stop iterating;
		# it has reached the end.
		raise StopIteration

	def updateEndingBoundaries(self):
		"""
		Recalculates rightX and bottomY using leftX, topY, width, and height
		@return: none
		"""
		self.rightX = self.leftX + self.width
		self.bottomY = self.topY + self.height

	def updateWH(self):
		"""
		Recalculates width and height using leftX, rightX, topY, and bottomY.
		@return: none
		"""
		self.width = self.rightX - self.leftX
		self.height = self.bottomY - self.topY

	def overlap(self, other, withinAmount):
		"""
		Determines whether the blob (itself) intersects with the given blob.
		withinAmount should be between 0 and 0.9, inclusive, but does not have to be.
		withinAmount is used to increase the chances of intersection: for each comparison
		between two fields of the blobs, one of those is multiplied by (1 + withinAmount) or
		(1 - withinAmount). Without a withinAmount larger than 0, it is unlikely that two blobs
		would ever intersect.

		@param other: The Blob to check for intersection with.
		@param withinAmount: The amount to increase or decrease a field by to increase chances of intersection.
							 Expected: 0 to 0.9, inclusive
		@return: True it the two Blobs overlap with each other; False if they don't.
		"""
		overlap = True
		increase = 1 + withinAmount
		decrease = 1 - withinAmount

		# If any of the comparisons are True, then the Blobs do not intersect.
		# If self.rightX < other.leftX, then self ends before other begins (in terms of x).
		#	 Multiplying self.rightX by increase increases the chances that this evaluates to false.
		# If self.leftX > other.rightX, then self starts after other begins (in terms of x).
		#	 Multiplying self.leftX by decrease increases the chances that this evaluates to false.
		if((self.rightX * increase) < other.leftX or (self.leftX * decrease) > other.rightX):
			overlap = False

		# If any of the comparisons are True, then the Blobs do not intersect.
		# If self.bottomY < other.topY, then self ends before other begins (in terms of y).
		#	 Multiplying self.bottomY by increase increases the chances that this evaluates to false.
		# If self.topY > other.bottomY, then self starts after other begins (in terms of y).
		#	 Multiplying self.topY by decrease increases the chances that this evaluates to false.
		if((self.bottomY * increase) < other.topY or (self.topY * decrease) > other.bottomY):
			overlap = False

		return overlap

	def scaleXYWH(self, currentArea, newWidth, newHeight):
		"""
		Scales the dimensions for a new width and height. This allows the clients to receive data
		according to the dimensions of their program. Returns the new dimensions as a tuple,
		(leftX, topW, width, height). This call does not change the fields of the blob itself.
		@param currentArea: the AreaOfInterest that the blob is in.
							The Blob can be in multiple areas of interest, and when the message
							string is being created, scaleXYWH will be called for each one.
							width and height, and leftX and topY of currentArea are used as part
							of the calculation to scale the coordinates.
		@param newWidth: the width to scale to.
		@param newHeight: the height to scale to.
		@return tuple, the scaled (leftX, topY, width, height) of the blob.
		"""

		# Save the fields into local variables so that they aren't changed.
		# Find the dimensions of the currentArea, and calculate the ratio of newDimension to currentDimension.
		x,y,w,h = self.leftX, self.topY, self.width, self.height
		currentWidth = currentArea.rightX - currentArea.leftX
		currentHeight = currentArea.bottomY - currentArea.topY
		#print("\ncurrentWidth " + currentWidth.__str__() + ", currentHeight " + currentHeight.__str__())
		#print(	 "newWidth	   " + newWidth.__str__() +		", newHeight	 " + newHeight.__str__())
		xChange = newWidth / float(currentWidth)
		yChange = newHeight / float(currentHeight)

		#print("\nxChange: " + xChange.__str__() + ", yChange: " + yChange.__str__())

		#print("\ncurrent area leftX " + currentArea.leftX.__str__() + ", current area topY " + currentArea.topY.__str__())
		#print("x change " + (currentArea.leftX - x).__str__() + ", y change " + (currentArea.topY - y).__str__())

		# The value of x should be in relation to the start of currentArea, not the start
		# of the image from the camera (as it currently is). Subtract currentArea.leftX
		# from x to get rid of the portion outside of currentArea. Then multiply the result
		# by the ratio found for converting from currentWidth to newWidth. The result is
		# a correctly scaled new starting x value.
		#print("\noriginal x:		   " + x.__str__())
		x = x - currentArea.leftX
		#print("partially updated x: " + x.__str__())
		x *= xChange
		#print("fully updated x:	 " + x.__str__())

		# The value of y should be in relation to the start of currentArea, not the start
		# of the image from the camera (as it currently is). Subtract currentArea.topY
		# from y to get rid of the portion outside of currentArea. Then multiply the result
		# by the ratio found for converting from currentHeight to newHeight. The result is
		# a correctly scaled new starting y value.
		#print("\noriginal y:		   " + y.__str__())
		y = y - currentArea.topY
		#print("partially updated y: " + y.__str__())
		y *= yChange
		#print("fully updated y:	 " + y.__str__())

		# If we scale the width of the blob and then add it to the newly scaled starting x, we
		# get the scaled ending x of the blob. Since the server sends messages using the starting
		# coordinates and a width and height, finding the scaled width is more efficient than
		# finding the scaled end, and then subtracting the scaled start to find the width.
		# (The same goes for y, and height)
		# w and h are simply the width and height of the Blob, so there is nothing to get rid of.
		# Simply multply them by the xChange and yChange ratios.
		#print("\noriginal width:  " + w.__str__())
		w = w * xChange
		#print("new height:		 " + w.__str__())
		#print("original height: " + h.__str__())
		h = h * yChange
		#print("new height:		 " + h.__str__())

		#print("\nstart x: " + x.__str__() + "\nend x:	 " + (x + w).__str__())
		#print("start y: " + y.__str__() + "\nend y:   " + (y + h).__str__())


		#print("\n\n\n")

		# Return the scaled data.
		return (x,y,w,h)


class Data:
	"""
	Stores and controls the data for the server; deals with formatting the data to
	send over the server socket, and with updating the GUI display.
	"""

	# Stores the areas on interest (instances of AreaOfInterest).
	interestList = []
	# Stores the current detected faces (instances of Blob).
	faceList = []
	# Stores the holes (currently unused).
	holeList = []
	# Stores the currently detected motion (instances of Blob).
	shellList = []

	# Width to scale the Blob coordinates to before sending the coordinates to clients.
	# (used to format data to the dimensions of a client program.) 
	scalingWidth = 800
	scalingHeight = 500
	# Dimensions of the iHart video feed.
	iHartWidth = 240
	iHartHeight = 180

	# Settings used to tweak performance. They can all be accessed through trackbars
	# while the program is running.
	#
	# motionThreshold: controls how different an area needs to be from
	#				   the running average to be considered motion.
	# blurValue: controls how much the image is blurred when finding motion
	#			 (this cuts down on false motion)
	# noiseReductionValue: when this is larger than 0, the white areas are dilated and
	#					   then eroded by the specified amount, eliminating areas that
	#					   are that size, or smaller. This is done before the coordinates
	#					   of the motion is extracted, and turned into instances of Blob.
	# dilationValue: this also dilates the white areas of the motion image, but it does not
	#				 does not erode them; it increases the size of the motion areas.
	# mergeDistance: this allows different areas of motion to merge with each other. By
	#				 their nature, no two areas of motion will actually overlap--if they
	#				 did, they would be one area of motion. mergeDistance is used to increase
	#				 the values of blobs to increase the chances that they overlap with each
	#				 other. When this happens, the two are combined into a new Blob, which
	#				 is put into shellList.
	motionThreshold = 20
	blurValue = 3
	noiseReductionValue = 0
	dilationValue = 0
	noiseKernel = None
	dilateKernel = None
	mergeDistance = 0.3

	# Determines whether should check for motion and/or faces, and whether the camera image
	# should be flipped horizontally (used for mirroring purposes). 
	motionEnabled = True
	facesEnabled = False
	flipHorizontal = False

	# Used for the creation of new areas of interest. Stores whether on is in progress, and
	# stores the currently-under-construction area of interest.
	creatingAreaOfInterest = False
	workingAreaOfInterest = None

	video = None
	difference = None
	average = None
	referenceShot = None
	videoCapture = None	 # = cv2.VideoCapture(0)
	width = 240
	height = 180
	vWindow = "server"
	mWindow = "motion"
	gWindow = "settings"
	hWindow = "help window"

	# The trackbars for the server settings. openCV uses strings to retrieve the different trackbars.
	motionTrackbar = "motion threshold"
	blurTrackbar = "blur value"
	noiseTrackbar = "reduce noise"
	dilateTrackbar = "increase blob size"
	quitTrackbar = "quit"
	facesTrackbar = "enable faces"
	motionEnableTrackbar = "enable motion"
	flipTrackbar = "flip horizontally"
	mergeTrackbar = "merge within distance"
	helpTrackbar = "help?"

	# Tracks whether the help window is open.
	helpOpen = False
	# The image the help window displays.
	helpImage = "mainHelp.png"

	def __init__(self, cameraIndex):
		"""
		Starts communication with the specified camera by getting a VideoCapture instance
		from openCV, but does not store an image from the video feed yet.
		@param cameraIndex: The index of the camera to communicate with
							(if there is only one camera, it will always be index 0)
		@return: none
		"""
		self.videoCapture = cv2.VideoCapture(cameraIndex)

	def addAreaOfInterest(self, leftX, rightX, topY, bottomY):
		"""
		Creates a new AreaOfInterest with the given data and adds it to interestList.
		@param leftX: The starting x coordinate of the area of interest.
		@param rightX: The ending x coordinate of the area of interest.
		@param topY: The starting y coordinate of the area of interest.
		@param bottomY: The starting y coordinate of the area of interest.
		@return: none
		"""
		toAdd = AreaOfInterest(leftX, rightX, topY, bottomY)
		list.append(self.interestList, toAdd)

	def getAreaOfInterest(self, index):
		"""
		Returns the area of interest at the specified interest.
		@param index: the index to retrieve.
		@return: the specified AreaOfInterest instance.
		"""
		return self.interestList[index]

	def createInformationString(self):
		"""
		Creates an information string to send to all of the client connections held by SocketHandler.
		The string contains each area of interest. For each area of interest, every blob of detected
		motion that is within that area is included, and then each face that is within that area. All
		coordinates are updated if the blob is only partially within the area of interest. All coordinates
		are scaled according to scalingWidth and scalingHeight (the dimensions of the client program)
		Calling this method in no way changes the state of memory: all lists are unchanged after the
		call (any changes made to coordinates only effect the output string: no Blob will have its
		fields changed).

		The format of the string itself is as follows:
		<area number>|<area information> <area number>|<area information>
			This repeats until the string ends with "\n\0"
				(if you are viewing in html, the string ends with "\ n \ 0" if you remove the spaces.)
			If there are no areas of interest, an empty string is returned.

			<area information> is formatted as follows:
				<shell (motion) information><face information>

				<shell (motion) information> is formatted as follows:
					Shells:<motion> <motion> ]
						<motion> appears for each detected motion within the area of interest.
						Shell information ends with the ] character.
						If there are no shells within the area of interest, <shell (motion) information>
						is entirely empty.
				<face information> is formatted as follows:
					Faces:<face> <face> ]
						<face> appears for each detected face within the area of interest.
						Face information ends with the ] character.
						If there are no shells within the area of interest, <face information>
						is entirely empty.
				<motion> and <face> are formatted as follows:
					leftX;topY;width;height;
					A space is included at the end of each <motion> or <face>

		Several examples:
			0|1|
				No motion blobs or faces were contained in either area of interest.
			0|Shells:260;136;332;200; ]1|Shells:135;0;415;400; ]
				One motion blob was in one area of interest, and one was in the other.
			0|Shells:0;0;214;630; ]Faces:63;138;639;213; ]1|Shells:0;20;428;105; ]
				Area 0 had a motion blob and a face, and Area 1 had a different motion blob and no faces.

		@return: the formatted message string.
		"""

		message = ""
		index = 0

		for area in self.interestList:
			# Formats the string for each area of interest.
			# Adds "<area number>|<area information>" to the current end of message.
			# The | character is only used within the string directly after an area of interest index.
			message += index.__str__() + "|"
			message += self.createAreaString(area)
			index += 1

		#print("final message is: " + message + "\n\n\n\n\n\n\n")
		# Adds characters to signal the end of the line/message. Java uses "\n" to signify end of line,
		# while Flash uses "\0"	  (Flash seems to be an exception to the rule in this.)
		return message + "\n" + "\0"

	def createAreaString(self, interestArea):
		"""
		Creates an information string containing all the data of the given AreaOfInterest
		(the data for all the areas of motion within the interest area, and then for all
		the faces within the interest area). All coordinates are updated if the blob is only
		partially within the area of interest. All coordinates are scaled according to scalingWidth
		and scalingHeight (the dimensions of the client program) Calling this method in no way
		changes the state of memory: all lists are unchanged after the call (any changes made to
		coordinates only effect the output string: no Blob will have its fields changed).

		The area string is formatted as follows:
			<shell (motion) information><face information>

			<shell (motion) information> is formatted as follows:
				Shells:<motion> <motion> ]
					<motion> appears for each detected motion within the area of interest.
					Shell information ends with the ] character.
					If there are no shells within the area of interest, <shell (motion) information>
					is entirely empty.
			<face information> is formatted as follows:
				Faces:<face> <face> ]
					<face> appears for each detected face within the area of interest.
					Face information ends with the ] character.
					If there are no shells within the area of interest, <face information>
					is entirely empty.
			<motion> and <face> are formatted as follows:
				leftX;topY;width;height;
				A space is included at the end of each <motion> or <face>

		@param interestArea: the AreaOfInterest that the string is being created for.
		@return: the formatted message string.
		"""

		temp = ""

		if (self.motionEnabled):
			# Format the information for all of the motion within the area of interest.
			temp += ""
			added = False

			for item in self.shellList:
				# Add each motion's information to the string if it is within interestArea.
				current = self.editBounds(item, interestArea)
				if current is not None:
					# Get the scaled coordinates of the current motion.
					scaled = current.scaleXYWH(interestArea, self.scalingWidth, self.scalingHeight)
					added = True
					# Add 'leftX;topY;width;height; ' to the information string.
					temp += scaled[0].__str__() + ";" + scaled[1].__str__() + ";" + \
							scaled[2].__str__() + ";" + scaled[3].__str__() + "; "

			# Only add the motion information if it isn't empty.
			if added:
				temp = "Shells:" + temp + "]"


		if (self.facesEnabled):
			# Format the information for all of the faces within the area of interest.
			temp2 = ""
			added = False

			for item in self.faceList:
				# Add each face's information to the string if it is within interestArea.
				current = self.editBounds(item, interestArea)
				if current is not None:
					# Get the scaled coordinates of the current motion.
					scaled = current.scaleXYWH(interestArea, self.scalingWidth, self.scalingHeight)
					added = True
					# Add 'leftX;topY;width;height; ' to the information string.
					temp2 += scaled[0].__str__() + ";" + scaled[1].__str__() + ";" + \
							 scaled[2].__str__() + ";" + scaled[3].__str__() + "; "

			# Only add the face information if it isn't empty.
			if added:
				temp += "Faces:" + temp2 + "]"

		return temp

	def editBounds(self, blob, interestArea):
		"""
		Determines whether the given Blob is within the given AreaOfInterest. If blob is outside of
		interestArea, returns None. If blob is fully within interestArea, returns blob. If blob is
		only partially within interestArea, returns a new Blob, cropped to only the portion within the
		interestArea. Calling this method in no way changes the state of blob, interestArea, or any
		other memory outside of this method and its return.

		@param blob: the Blob to test for presence within interestArea.
		@param interestArea: the AreaOfInterest to look for blob within.
		@return: an instance of Blob if blob is within interestArea; None otherwise.
		"""

		# If changed is False at the end, we can just return blob.
		# Initialize newBlob with the same data as blob, so that we only need to set changed fields
		# later, if newBlob is needed.
		changed = False
		newBlob = Blob(blob.leftX, blob.rightX, blob.topY, blob.bottomY, blob.width, blob.height)

		# If blob is entirely outside of interestArea, return None.
		if (blob.leftX > interestArea.rightX or blob.rightX < interestArea.leftX):
			# (blob starts (in terms of x) after interestArea ends, or vice versa)
			return None
		if (blob.topY > interestArea.bottomY or blob.bottomY < interestArea.topY):
			# (blob starts (in terms of y) after interestArea ends, or vice versa)
			return None


		# Determine whether blob is only partially within interestArea, and update newBlob's
		# corresponding field(s) if so.
		if (blob.leftX < interestArea.leftX):
			# In terms of X, blob starts before interestArea
			# does--change newBlob to start at interestArea.
			newBlob.leftX = interestArea.leftX
			changed = True

		if (blob.rightX > interestArea.rightX):
			# In terms of X, blob ends after interestArea
			# does--change newBlob to end at interestArea.
			newBlob.rightX = interestArea.rightX
			changed = True

		if (blob.topY < interestArea.topY):
			# In terms of Y, blob starts before interestArea
			# does--change newBlob to start at interestArea.
			newBlob.topY = interestArea.topY
			changed = True

		if (blob.bottomY > interestArea.bottomY):
			# In terms of Y, blob ends after interestArea
			# does--change newBlob to end at interestArea.
			newBlob.bottomY = interestArea.bottomY
			changed = True

		# Some fields were updated.
		if changed:
			# If the fields have been updated, the width and height are incorrect; update them.
			newBlob.updateWH()
			return newBlob
		# No fields were updated.
		else:
			return blob

	def drawAreasOfInterest(self):
		"""
		Draw all areas of interest.
		@return:
		"""

		for area in self.interestList:
			# Draws a rectangle on the video window from (x,y) to (x2,y2), in the specified color
			# (in BGR, the default color format of openCV)
			cv2.rectangle(self.video, (area.leftX, area.topY), (area.rightX, area.bottomY), (255, 194, 31))

	def drawFaces(self):
		"""
		Draw all the faces.
		@return: none
		"""

		for face in self.faceList:
			# Draws a rectangle on the video window from (x,y) to (x2,y2), in the specified color
			# (in BGR, the default color format of openCV)
			cv2.rectangle(self.video, (face.leftX, face.topY), (face.rightX, face.bottomY), (125, 213, 29))

	def drawMotion(self):
		"""
		Draw all the areas of motion.
		@return: none
		"""

		for shell in self.shellList:
			# Draws a rectangle on the video window from (x,y) to (x2,y2), in the specified color
			# (in BGR, the default color format of openCV)
			cv2.rectangle(self.video, (shell.leftX, shell.topY), (shell.rightX, shell.bottomY), (59, 234, 253))

	def updateVideo(self):
		"""
		Updates current video capture, and flips it horizontally if flipHorizontal is currently enabled.
		@return: none
		"""

		# Attempts to read the next image from the video feed.
		_, video = self.videoCapture.read()
		# openCV requires a wait after attempting to read (does not always need to be right after,
		# but cuts back on unreliable behavior to have it directly after read()).
		cv2.waitKey(50)

		# Loops until an image is captured from the video feed.
		while(video is None):
			_, video = self.videoCapture.read()
			cv2.waitKey(50)
		# updates the current image
		self.video = video

		# flips the image if flipHorizontal is enabled
		if self.flipHorizontal:
			# 1 denotes that should flip horizontally, not vertically
			self.video = cv2.flip(self.video, 1)

	def updateVideoAndGUI(self):
		"""
		Updates the current image from the video feed and displays it.
		@return: none
		"""
		self.updateVideo()
		# displays the image, self.video, on the video window, self.vWindow
		cv2.imshow(self.vWindow, self.video)

		# waiting is not strictly necessary, because updateVideo() waits, but waiting decreases openCV errors.
		cv2.waitKey(10)

	def updateGUI(self):
		"""
		Displays the current captured image (the most recent) on the video window.
		@return:
		"""

		# displays the image, self.video, on the video window, self.vWindow
		cv2.imshow(self.vWindow, self.video)

	def resetAreas(self):
		"""
		Deletes all the current areas of interest.
		@return: none
		"""
		self.interestList = []

	def mouseClicked(self, event, x, y, flags, extraParameter):
		"""
		Responds to left mouse click (cv2.EVENT_LBUTTONDOWN), mouse move/drag (cv2.EVENT_MOUSEMOVE),
		and mouse release (cv2.EVENT_LBUTTONUP) to create an AreaOfInterest. Allows the user to drag
		in any direction to create the AreaOfInterest, and does not create the AreaOfInterest if it
		is less than a certain size (at which point the box on the window will be drawn in red).
		Responds to right mouse click (cv2.EVENT_RBUTTONDOWN) by removing an area of interest.
		@param event: the mouse event.
		@param x: the x coordinate of the mouse.
		@param y: the y coordinate of the mouse.
		@param flags: unused (present for correct function signature)
		@param extraParameter: unused (present for correct function signature)
		@return: none
		"""

		# Left mouse click.
		if event == cv2.EVENT_LBUTTONDOWN:
			# Create the first point of the AreaOfInterest.
			self.creatingAreaOfInterest = True
			self.workingAreaOfInterest = AreaOfInterest(x, None, y, None)

		# An AreaOfInterest is already in the midst of being created; either the mouse has been
		# moved, or the button has been released.
		elif self.creatingAreaOfInterest:
			# Get the coordinates of the first point (the left mouse click).
			leftX = self.workingAreaOfInterest.leftX
			topY = self.workingAreaOfInterest.topY

			# leftX and topY represent the starting point of the AreaOfInterest, but it is
			# possible that the x or y of the new mouse location is less than the x or y
			# of the first. If this is the case, switch the two fields in question.
			# Do not write back to the AreaOfInterest until the mouse button is released:
			# no coordinates from moving stage should be saved. We do not yet know if there
			# is a mouse release or a mouse move event.
			if leftX > x:
				rightX = leftX
				leftX = x
			else:
				rightX = x
			if topY > y:
				bottomY = topY
				topY = y
			else:
				bottomY = y

			# Determine how far the mouse is from its original position.
			# If both x and y have changed by less than 10, the AreaOfInterest
			# should not be created.
			xChange = rightX - leftX
			yChange = bottomY - topY

			# The mouse has been released; finalize and add the AreaOfInterest
			# to interestList, if appropriate.
			if event == cv2.EVENT_LBUTTONUP:
				# Create the second point.

				# Either the AreaOfInterest will be completed after this method returns, or discarded.
				self.creatingAreaOfInterest = False
				# Only add the AreaOfInterest if it is larger than 10 units in either x or y.
				if xChange > 10 and yChange > 10:
					# Set the coordinates of the AreaOfInterest.
					# Rewrite all fields, in case two or more fields were swapped above (ie, user did not drag
					# diagonally down and to the right).
					self.workingAreaOfInterest.leftX = leftX
					self.workingAreaOfInterest.rightX = rightX
					self.workingAreaOfInterest.topY = topY
					self.workingAreaOfInterest.bottomY = bottomY

					# Add the area to the list and draw it on the video window.
					# (give cv2.rectangle image to draw on, (starting X, starting Y),
					#	(ending X, ending Y), (B,G,R) color.
					self.interestList.append(self.workingAreaOfInterest)
					cv2.rectangle(self.video, (self.workingAreaOfInterest.leftX, self.workingAreaOfInterest.topY),
							  (self.workingAreaOfInterest.rightX, self.workingAreaOfInterest.bottomY), (255, 194, 31))

			# The mouse has been moved.
			elif event == cv2.EVENT_MOUSEMOVE and self.creatingAreaOfInterest:
				# Temporarily draw rectangle (for incomplete area of interest)
				# If both x and y change are less than 10, draw in red--the AreaOfInterest won't
				# be saved if the user lets go now. Otherwise, draw in blue. Color format for openCV
				# is BGR.
				# (give cv2.rectangle image to draw on, (starting X, starting Y),
				#	(ending X, ending Y), (B,G,R) color.
				if xChange < 10 and yChange < 10:
					cv2.rectangle(self.video, (leftX, topY), (rightX, bottomY), (0, 87, 239))
				else:
					cv2.rectangle(self.video, (leftX, topY), (rightX, bottomY), (255, 194, 31))
		# Right mouse click.
		elif event == cv2.EVENT_RBUTTONDOWN:
			# Find out if the click event happened inside one or more areas of interest.
			# If it did, remove the most recently created area of interest that was affected.
			toRemove = None
			for aoi in self.interestList:
				# y is measured from the top (0) to the bottom (larger positive numbers)
				if aoi.leftX <= x and x <= aoi.rightX and aoi.bottomY >= y and y >= aoi.topY:
					toRemove = aoi
			if toRemove in self.interestList:
				self.interestList.remove(toRemove)
		# Redraw self.video on vWindow.
		cv2.imshow(self.vWindow, self.video)	

	def updateTrackbars(self, x):
		"""
		Responds to movement of the trackbars by updating the appropriate settings.
		@param x: unused (present for correct signature)
		@return: none
		"""

		# If the quit trackbar is on 1, exit the program.
		if cv2.getTrackbarPos(self.quitTrackbar, self.gWindow) == 1:
			cv2.destroyAllWindows()
			self.videoCapture.release() # destroy the video capture separately
			sys.exit()

		# facesEnabled, motionEnabled, and flipHorizontal should all be True if their
		# trackbars are set to 1, and False otherwise.
		self.facesEnabled = (cv2.getTrackbarPos(self.facesTrackbar, self.gWindow) == 1)
		self.motionEnabled = (cv2.getTrackbarPos(self.motionEnableTrackbar, self.gWindow) == 1)
		self.flipHorizontal = (cv2.getTrackbarPos(self.flipTrackbar, self.gWindow) == 1)

		# motionThreshold, blurValue, noiseReductionValue, and dilationValue should all
		# equal the same thing as the trackbar position. blurValue is increased by 1 because
		# it should never be 0.
		self.motionThreshold = cv2.getTrackbarPos(self.motionTrackbar, self.gWindow)
		self.blurValue = cv2.getTrackbarPos(self.blurTrackbar, self.gWindow) + 1
		self.noiseReductionValue = cv2.getTrackbarPos(self.noiseTrackbar, self.gWindow)
		self.dilationValue = cv2.getTrackbarPos(self.dilateTrackbar, self.gWindow)

		# Format mergeDistance, which needs to be divided by 10.0, or result will be rounded to an int
		# (or could surround one side with float(), but not the entire statement)
		# mergeDistance will range from 0 to 0.9, inclusive.
		self.mergeDistance = cv2.getTrackbarPos(self.mergeTrackbar, self.gWindow) / 10.0

		# Create a new Kernel (for increasing or decreasing blobs (after threshold is applied) with openCV)
		# only if the size is more than 0: if it is 0, the program will crash.
		if self.noiseReductionValue > 0:
			self.noiseKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (self.noiseReductionValue, self.noiseReductionValue))
		if self.dilationValue > 0:
			self.dilateKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (self.dilationValue, self.dilationValue))

		# If the help trackbar is on 1, the help window should be displayed.
		if cv2.getTrackbarPos(self.helpTrackbar, self.gWindow) == 1 and not self.helpOpen:
			cv2.namedWindow(self.hWindow)
			image = cv2.imread(self.helpImage)
			cv2.imshow(self.hWindow, image)
			self.helpOpen = True
		# If the help window was displayed, but the help trackbar is no longer on 1, close the widnow.
		elif cv2.getTrackbarPos(self.helpTrackbar, self.gWindow) == 0 and self.helpOpen:
			cv2.destroyWindow(self.hWindow)
			self.helpOpen = False

	def createGUI(self):
		"""
		Create the GUI for cvServer: video feed window, motion window, and settings window. Set the
		video window to listen to mouse events, and add all the trackbars to the settings window.
		@return: none
		"""

		# Create the window for the video feed and the one for motion, and resize the windows
		# (otherwise they start off with only the bar for closing, maximizing, and minimizing,
		# and when one gets an image from the camera it jumps to full-screen without any way to
		# resize it using the mouse).
		cv2.namedWindow(self.vWindow)
		cv2.resizeWindow(self.vWindow, self.iHartWidth, self.iHartHeight)
		cv2.namedWindow(self.mWindow)
		cv2.resizeWindow(self.mWindow, self.iHartWidth, self.iHartHeight)

		# Create a window for the settings trackbars and resize it.
		cv2.namedWindow(self.gWindow)
		cv2.resizeWindow(self.gWindow, 550, 150)

		# Create all the trackbars, put them all in gWindow, and set them all to use updateTrackbars
		# as their action listener.
		# createTrackbar takes the following arguments:
		#	variable for the trackbar to be stored in, window to appear on, value to start at (not minimum value),
		#	maximum value, and action listener method.
		# Trackbars' minimum value is always 0.
		# (With openCV's GUI, there are no buttons so trackbars with only two options substitute for them).
		cv2.createTrackbar(self.motionTrackbar, self.gWindow, self.motionThreshold, 50, self.updateTrackbars)
		cv2.createTrackbar(self.blurTrackbar, self.gWindow, self.blurValue, 20, self.updateTrackbars)
		cv2.createTrackbar(self.noiseTrackbar, self.gWindow, self.noiseReductionValue, 20, self.updateTrackbars)
		cv2.createTrackbar(self.dilateTrackbar, self.gWindow, self.dilationValue, 20, self.updateTrackbars)
		cv2.createTrackbar(self.facesTrackbar, self.gWindow, 0, 1, self.updateTrackbars)
		cv2.createTrackbar(self.quitTrackbar, self.gWindow, 0, 1, self.updateTrackbars)
		cv2.createTrackbar(self.motionEnableTrackbar, self.gWindow, 1, 1, self.updateTrackbars)
		cv2.createTrackbar(self.flipTrackbar, self.gWindow, 0, 1, self.updateTrackbars)
		cv2.createTrackbar(self.helpTrackbar, self.gWindow, 0, 1, self.updateTrackbars)
		cv2.createTrackbar(self.mergeTrackbar, self.gWindow, int(self.mergeDistance*10), 9, self.updateTrackbars)

		# Add an action listener to the video feed window.
		cv2.setMouseCallback(self.vWindow, self.mouseClicked, None)

		# The method set is used to set different properties of the VideoCapture instance.
		# 3 determines that the width should be set; 4, the height.
		# (3 is CV_CAP_PROP_FRAME_WIDTH, and 4 is CV_CAP_PROP_FRAME_HEIGHT, but the aliases don't work)
		# This re-sizes the video received from VideoCapture.
		# After setting the properties, call method to read in an image from the feed and display it.
		self.videoCapture.set(3, self.width)
		self.videoCapture.set(4, self.height)
		self.updateVideoAndGUI()


class Server:
    """
    Runs the program by searching for motion and faces, updating the GUI, and sending information
    to any programs listening to the server socket (in SocketHandler).
    """
    data = None
    timer = None
    average = None
    kernelSize = 3
    cameraIndex = 0
    cameraTrackbar = "camera index"
    cameraChosenTrackbar = "start program"
    helpTrackbar = "help?"
    startQuitTrackbar = "quit"
    helpOpen = False
    sWindow = "start"
    hWindow = "help window"
    helpImage = "startupHelp.png"
    server = None


    def __init__(self):
        """
        Creates a new window so that the user can set the camera index to use, and waits
        until the user drags the start trackbar to 1, starting the rest of the program.
        @return: none
        """

        # Creates the window and gives it a size (otherwise, its width and height is 0).
        cv2.namedWindow(self.sWindow)
        cv2.resizeWindow(self.sWindow, 100, 40)

        # Adds a trackbar for choosing the camera index, a trackbar for starting the program, and a trackbar
        # for displaying a help image. (With openCV's GUI, there are no buttons so trackbars with only
        # two options substitute for them).
        # createTrackbar takes the following arguments:
        #   variable for the trackbar to be stored in, window to appear on, value to start at (not minimum value),
        #   maximum value, and action listener method.
        cv2.createTrackbar(self.cameraTrackbar, self.sWindow, self.cameraIndex, 5, self.decideCameraTrackbars)
        cv2.createTrackbar(self.cameraChosenTrackbar, self.sWindow, 0, 1, self.decideCameraTrackbars)
        cv2.createTrackbar(self.helpTrackbar, self.sWindow, 0, 1, self.decideCameraTrackbars)
        cv2.createTrackbar(self.startQuitTrackbar, self.sWindow, 0, 1, self.decideCameraTrackbars)

        # This prevents the window from closing immediately; without it, we reach the end of our
        # code because the rest (including the infinite loop which keeps everything updating) is
        # called once the user drags the trackbar to start.
        cv2.waitKey(1000000)

    def updateGUI(self):
        """
        Updates the GUI.
        @return: none
        """
        self.data.updateVideoAndGUI()

    def detectMotion(self):
        """
        Searches for motion in the video feed; puts the found motion in data.shellList (instances of Blob).
        @return: none
        """

        # Creates average, if it doesn't yet exist.
        if (self.data.average is None):
            # Though it represents an image, it is an image converted to numpy.float32
            self.data.average = numpy.float32(self.data.video)

        if self.data.blurValue != 0:
            # Blurs the image to reduce noise and smooth found motion.
            # Blur value controls the strength of the blur.
            self.data.difference = cv2.blur(self.data.video, (self.data.blurValue, self.data.blurValue))

        # (not sure about this line's necessity) added because there were different types in absdiff
        self.data.difference = numpy.float32(self.data.difference)

        # Add difference to the running average of frames. (last argument determines
        # how fast images fade from the average.)
        cv2.accumulateWeighted(self.data.difference, self.data.average, 0.320)

        # Calculates absolute difference of difference from the average.
        self.data.difference = cv2.absdiff(self.data.difference, self.data.average)

        # Converts the image to grayscale.
        self.data.difference = cv2.cvtColor(self.data.difference, cv2.COLOR_BGR2GRAY, self.data.difference, 0)

        if self.data.blurValue != 0:
            # Blurs the image to reduce noise and smooth found motion.
            # Blur value controls the strength of the blur.
            self.data.difference = cv2.blur(self.data.difference, (self.data.blurValue, self.data.blurValue))

        # Applies thresholding so every pixel is black or white (white for movement)
        _, self.data.difference = cv2.threshold(self.data.difference, self.data.motionThreshold, 255, cv2.THRESH_BINARY)

        if self.data.noiseReductionValue != 0:
            # Erodes and then dilates the blobs, to eliminate extra white noise.
            # (any blobs smaller than noiseReductionValue will be erased)
            self.data.difference = cv2.morphologyEx(self.data.difference, cv2.MORPH_OPEN, self.data.noiseKernel)
        if self.data.dilationValue != 0:
            # Dilates the blobs (increasing the size of detected motion)
            self.data.difference = cv2.dilate(self.data.difference, self.data.dilateKernel)


        # OpenCV documentation includes CV_ in various arguments, such as CV_RETR_EXTERNAL,
        # but the recognized name does not (get an error when attemp to use the one from documentation).
        #
        # first parameter: the image to process. astype is crucial: without it, opencv has type errors.
        #                  we could use cv2.RETR_CCOMP to give us holes and external contours, but this
        #                  would be pointless since we go on to merge blobs where possible. Additionally,
        #                  they would not be very useful for implementing holes, because creating holes in
        #                  motion would be difficult.
        # second parameter: (mode) finds the outer contours and gives them a one level hierarchy.
        # third parameter: compresses contours horizontally and vertically, into 4 points
        contours, hierarchy  = cv2.findContours(self.data.difference.astype('uint8'), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )

        # Display difference on the motion window, to show the motion. (this is in addition to drawing
        # rectangles for the motion on the video window later).
        cv2.imshow(self.data.mWindow, self.data.difference)

        # Turn the raw data into Blobs, and merge them together when possible (according to mergeDistance)
        self.editDetectedMotion(contours, hierarchy)

    def editDetectedMotion(self, contours, hierarchy):
        """
        Turns the raw motion data into instances of Blob and stores them in data.shellList
        after also merging them when they are within mergeDistance of each other.
        @param contours: the raw data for the motion.
        @param hierarchy: the hierarchy of the contours.
        @return: none
        """

        # Reset shellList to erase previously found shells. (otherwise there would be duplicates)
        shellList = []

        # Add a blob for each contour
        for contour in contours:
            # Each contour has been compressed into four points, but we don't have easy access to
            # that data. boundingRect allows us to access it. Additionally, the four points might
            # be tilted (as in, the rectangle is not upright), but we want an upright rectangle for
            # collision/overlap purposes, in addition to the fact that our client programs expect it.
            x, y, w, h = cv2.boundingRect(contour)
            # the omitted fields are filled in by Blob.
            shellList.append(Blob(x, -1, y, -1, w, h))

        # Merge the Blobs together, when possible.
        self.mergeOverLappingMotion(shellList)
        # Give data the updated shells.
        self.data.shellList = shellList

    def mergeOverLappingMotion(self, shellList):
        """
        Combines blobs when they are within data.mergeDistance of each other. mergeDistance is
        from 0 to 0.9, inclusive, and mergeOverlappingMotion multiplies the coordinates of blobs
        by 1 + mergeDistance or 1 - mergeDistance in order to increase chances of overlap. When the
        two blobs in question do overlap, they are combined into one blob, which is placed into the
        list (shellList) in their stead. The process is repeated until no more overlapping blobs are found.
        @param shellList: the list of blobs to attempt to combine.
        @return: none
        """

        for shell in shellList:
            # compare each shell in shellList to every other shell in shellList
            for other in shellList:

                if shell is other:
                    # Continue to next iteration of the inner loop (walk past oneself).
                    continue

                # The blob itself performs the analysis to find whether it overlaps with
                # the other, given blob when overlap is increased by mergeDistance.
                overlap = shell.overlap(other, self.data.mergeDistance)

                if overlap:
                    # For the starting fields (leftX and topY), store the lowest value of the two in the new blob.
                    # For the ending fields (rightX and bottomY), store the highest value of the two in the new blob.
                    leftX = min(shell.leftX, other.leftX)
                    topY = min(shell.topY, other.topY)
                    rightX = max(shell.rightX, other.rightX)
                    bottomY = max(shell.bottomY, other.bottomY)

                    # Remove the two now-combined blobs from the list.
                    shellList.remove(shell)
                    shellList.remove(other)
                    # Add the new, combined blob to the list.
                    shellList.append(Blob(leftX, rightX, topY, bottomY, -1, -1))

                    # Restart the process of combining the blobs: this is necessary because
                    # we have removed elements from the list, breaking our iteration over it.
                    # Additionally, the combined blob might intersect with another blob, where the
                    # original two would not.
                    return self.mergeOverLappingMotion(shellList)

    def detectFaces(self):
        """
        Searches for faces in the current image from the video feed and stores them in data.faceList
        (as instances of Blob).
        @return: none
        """

        # Load the face recognition file into opencv.
        faceType = "haarcascade_frontalface_alt.xml"
        faceClassifier = cv2.CascadeClassifier()
        faceClassifier.load(faceType)

        # Convert the image to grayscale so that opencv can search for faces.
        grayImage = cv2.cvtColor(self.data.video, cv2.COLOR_BGR2GRAY)

        # Look for faces at all scales (otherwise, would look for a certain size face)
        # Edit the raw data into instances of Blob (and put them into data.faceList).
        rawFaceList = faceClassifier.detectMultiScale(grayImage)
        self.editFaces(rawFaceList)

    def editFaces(self, rawFaceList):
        """
        Convert the raw face data into instances of Blob, stored in data.faceList.
        @param rawFaceList: the raw face data returned from detectMultiScale.
        @return: none
        """

        # Erase any previously found faces, to eliminate duplicates.
        self.data.faceList = []
        for face in rawFaceList:
            # Put the face data into a Blob instance and add it to faceList.
            blob = Blob(face[0], -1, face[1], -1, face[2], face[3])
            self.data.faceList.append(blob)

    def createGUI(self):
        """
        Create the GUI for the server.
        @return: none
        """
        self.data.createGUI()

    def decideCameraTrackbars(self, x):
        """
        Set the camera index to use, display a help menu when requested, and start
        the rest of the program when prompted.
        @param x: unused parameter; remains for method signature to be correct.
        @return: none
        """
        if cv2.getTrackbarPos(self.cameraChosenTrackbar, self.sWindow) == 1:
            # The start trackbar has been dragged to 1; store the camera index and start the program.
            self.cameraIndex = cv2.getTrackbarPos(self.cameraTrackbar, self.sWindow)
            self.data = Data(self.cameraIndex)
            # Initialize the SocketHandler, which will create the server socket.
            self.server = SocketHandler()
            # Close the camera index window.
            cv2.destroyWindow(self.sWindow)
            # Create the GUI to display video feed, motion, and settings.
            self.createGUI()
            # Start the continuous loop that will run the rest of the program.
            self.run()
            
        if cv2.getTrackbarPos(self.startQuitTrackbar, self.sWindow) == 1:
        	# the quit trackbar has been dragged to 1; quit the program.
        	cv2.destroyAllWindows()
        	sys.exit()
		
        if cv2.getTrackbarPos(self.helpTrackbar, self.sWindow) == 1 and not self.helpOpen:
            # Open the help window and display the help image on it.
            cv2.namedWindow(self.hWindow)
            # The image needs to first  be read into opencv, and then displayed.
            image = cv2.imread(self.helpImage)
            cv2.imshow(self.hWindow, image)
            self.helpOpen = True
            # Wait so that the window doesn't disappear.
            cv2.waitKey(100000)
        elif self.helpOpen:
            # Close the help window.
            cv2.destroyWindow(self.hWindow)
            self.helpOpen = False

    def run(self):
        """
        Searches the video feed for faces and motion, draws items onto the display,
        updates the display, and sends messages from the server socket to any waiting
        clients (using SocketHandler).
        (The only way to escape the loop is to drag the quit trackbar to 1).

        @return: none
        """
        while (True):
            # Update the current image from the video, but don't display it yet.
            # Displaying it now would cause a flashing display, because we'll draw
            # rectangles on it for interest areas, motion, and faces later.
            # (If we showed it now, and then after drawing, it would flash between
            # rectangles and no rectangles, because drawing happens on the image,
            # not on the window itself).
            self.data.updateVideo()

            # Detect and draw motion if it is enabled.
            if self.data.motionEnabled:
                self.detectMotion()
                self.data.drawMotion()
            # Detect and draw faces if they are enabled.
            if self.data.facesEnabled:
                self.detectFaces()
                self.data.drawFaces()
            # Draw the areas of interest.
            self.data.drawAreasOfInterest()

            # Now that drawing is done, update the display.
            self.data.updateGUI()

            # Get the message string, encoding all the relevant interest area and blob data.
            message = self.data.createInformationString()

            # Have the socket check for new incoming connections. Since we don't know how
            # many clients we'll have, or when they'll connect, we check each time. Normally
            # this call would block until it found an incoming connection, but the SocketHandler
            # sets the socket to be non-blocking.
            # Once any new clients have been accepted, send all of the clients the message string.
            self.server.checkIncomingConnections()
            self.server.sendInformation(message)

if __name__ == "__main__":
	# Starts the program.
	s = Server()