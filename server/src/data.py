"""
Responsible for:
    * Storing data for the server
    * Formating Blob data into strings (that are sent via the SocketHandler to clients)
    * Updating the GUI
"""

# External module dependencies
import cv2      # openCV
import json     # JSON library for message encoding
import sys      # so that we can exit()

# Project deprendencies
from area_of_interest import AreaOfInterest
from blob import Blob
from utility import *
import gui as gui

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
    #                  the running average to be considered motion.
    # blurValue: controls how much the image is blurred when finding motion
    #            (this cuts down on false motion)
    # noiseReductionValue: when this is larger than 0, the white areas are dilated and
    #                      then eroded by the specified amount, eliminating areas that
    #                      are that size, or smaller. This is done before the coordinates
    #                      of the motion is extracted, and turned into instances of Blob.
    # dilationValue: this also dilates the white areas of the motion image, but it does not
    #                does not erode them; it increases the size of the motion areas.
    # mergeDistance: this allows different areas of motion to merge with each other. By
    #                their nature, no two areas of motion will actually overlap--if they
    #                did, they would be one area of motion. mergeDistance is used to increase
    #                the values of blobs to increase the chances that they overlap with each
    #                other. When this happens, the two are combined into a new Blob, which
    #                is put into shellList.
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
    videoCapture = None  # = cv2.VideoCapture(0)
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

        The format of the string itself is as follows (spaces added for readability):
            [ <area information>, <area information>, ... ]
        This repeats until the string ends with "\n\0"
            (if you are viewing in html, the string ends with "\ n \ 0" if you remove the spaces.)
        The index of the <area information> corresponds to the number of the area of interest.
        If there are no areas of interest, an empty string is returned.

        <area information> is formatted as follows:
            {
                "Faces": [ <face information>, <face information>, ... ],
                "Shells": [ <shell information>, <shell information>, ... ]
            }

        <shell (motion) information> and <face information> are both formatted the same,
        since they both represent rectangles of detected motion. The format is as
        follows:
            [ leftX, topY, width, height ]
        We use a list since JSON does not use tuples.

        Several examples:
            [ { "Faces": [], "Shells": [] }, { "Faces": [], "Shells": [] } ]
                No motion blobs or faces were contained in either area of interest.

            [ { "Faces": [], "Shells": [ [ 260, 136, 332, 200] ] },
              { "Faces": [], "Shells": [ [ 135, 0, 415, 400 ] ] } ]
                One motion blob was in one area of interest, and one was in the other.

            [ { "Faces": [ [ 63, 138, 639, 213 ] ], "Shells": [ [ 0, 0, 214, 630 ] ] },
              { "Faces": [], "Shells": [ [ 0, 20, 428, 105 ] ] } ]
                Area 0 had a motion blob and a face, and Area 1 had a different motion blob and no faces.

        @return: the formatted message string.
        """

        areaData = []

        for area in self.interestList:
            # Formats the string for each area of interest.
            areaData.append(self.createAreaData(area))

        # Use the JSON library to dump the list of area information into a JSON-formatted string.
        message = json.dumps(areaData)

        # Adds characters to signal the end of the line/message. Java uses "\n" to signify end of line,
        # while Flash uses "\0"   (Flash seems to be an exception to the rule in this.)
        return message + "\n" + "\0"

    def createAreaData(self, interestArea):
        """
        Creates an information string containing all the data of the given AreaOfInterest
        (the data for all the areas of motion within the interest area, and then for all
        the faces within the interest area). All coordinates are updated if the blob is only
        partially within the area of interest. All coordinates are scaled according to scalingWidth
        and scalingHeight (the dimensions of the client program) Calling this method in no way
        changes the state of memory: all lists are unchanged after the call (any changes made to
        coordinates only effect the output string: no Blob will have its fields changed).

        The area string is formatted as follows:
            {
                "Faces": [ <face information>, <face information>, ... ],
                "Shells": [ <shell information>, <shell information>, ... ]
            }

        <shell (motion) information> and <face information> are both formatted the same,
        since they both represent rectangles of detected motion. The format is as
        follows:
            [ leftX, topY, width, height ]
        We use a list since JSON does not use tuples.

        @param interestArea: the AreaOfInterest that the string is being created for.
        @return: the formatted message string.
        """

        temp = {
            "Shells": [],
            "Faces": []
        }

        if self.motionEnabled:
            # Format the information for all of the motion within the area of interest.
            for item in self.shellList:
                # Add each motion's information to the string if it is within interestArea.
                current = self.editBounds(item, interestArea)
                if current is not None:
                    # Get the scaled coordinates of the current motion.
                    scaled = current.scaleXYWH(interestArea, self.scalingWidth, self.scalingHeight)
                    # Add [leftX, topY, width, height] to the object.
                    temp["Shells"].append(scaled)

        if self.facesEnabled:
            # Format the information for all of the faces within the area of interest.
            for item in self.faceList:
                # Add each face's information to the string if it is within interestArea.
                current = self.editBounds(item, interestArea)
                if current is not None:
                    # Get the scaled coordinates of the current face.
                    scaled = current.scaleXYWH(interestArea, self.scalingWidth, self.scalingHeight)
                    # Add [leftX, topY, width, height] to the object.
                    temp["Faces"].append(scaled)

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
                    #   (ending X, ending Y), (B,G,R) color.
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
                #   (ending X, ending Y), (B,G,R) color.
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
        self.facesEnabled = gui.enable
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
            image = cv2.imread(resource_path(self.helpImage))
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

        # # Create a window for the settings trackbars and resize it.
        # cv2.namedWindow(self.gWindow, flags=cv2.WINDOW_NORMAL)
        # cv2.resizeWindow(self.gWindow, 550, 150)
        #
        # # Create all the trackbars, put them all in gWindow, and set them all to use updateTrackbars
        # # as their action listener.
        # # createTrackbar takes the following arguments:
        # #   variable for the trackbar to be stored in, window to appear on, value to start at (not minimum value),
        # #   maximum value, and action listener method.
        # # Trackbars' minimum value is always 0.
        # # (With openCV's GUI, there are no buttons so trackbars with only two options substitute for them).
        # cv2.createTrackbar(self.motionTrackbar, self.gWindow, self.motionThreshold, 50, self.updateTrackbars)
        # cv2.createTrackbar(self.blurTrackbar, self.gWindow, self.blurValue, 20, self.updateTrackbars)
        # cv2.createTrackbar(self.noiseTrackbar, self.gWindow, self.noiseReductionValue, 20, self.updateTrackbars)
        # cv2.createTrackbar(self.dilateTrackbar, self.gWindow, self.dilationValue, 20, self.updateTrackbars)
        # cv2.createTrackbar(self.facesTrackbar, self.gWindow, 0, 1, self.updateTrackbars)
        # cv2.createTrackbar(self.quitTrackbar, self.gWindow, 0, 1, self.updateTrackbars)
        # cv2.createTrackbar(self.motionEnableTrackbar, self.gWindow, 1, 1, self.updateTrackbars)
        # cv2.createTrackbar(self.flipTrackbar, self.gWindow, 0, 1, self.updateTrackbars)
        # cv2.createTrackbar(self.helpTrackbar, self.gWindow, 0, 1, self.updateTrackbars)
        # cv2.createTrackbar(self.mergeTrackbar, self.gWindow, int(self.mergeDistance*10), 9, self.updateTrackbars)

        # self.gui = App(self.updateMotion, self.updateBlur, etc etc etc)
        # like updateTrackbar
        # def updateMotion(self, newVal): do something

        # Add an action listener to the video feed window.
        cv2.setMouseCallback(self.vWindow, self.mouseClicked, None)

        # Add an initial default area of interest that encompasses the entire screen.
        # Although we set them to 240 by 180, they turn out to be 320 by 240 on Windows,
		# but 240 by 180 on OS X.
        self.addAreaOfInterest(3, 237, 3, 173)

        # The method set is used to set different properties of the VideoCapture instance.
        # 3 determines that the width should be set; 4, the height.
        # (3 is CV_CAP_PROP_FRAME_WIDTH, and 4 is CV_CAP_PROP_FRAME_HEIGHT, but the aliases don't work)
        # This re-sizes the video received from VideoCapture.
        # After setting the properties, call method to read in an image from the feed and display it.
        self.videoCapture.set(3, self.width)
        self.videoCapture.set(4, self.height)
        self.updateVideoAndGUI()
