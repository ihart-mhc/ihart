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

# External module dependencies
import argparse # to parse command-line arguments
# Tkinter has to initialize before numpy/cv2/anything else, otherwise we get an NSInvalidArgumentException.
# Hence we import Tkinter first and let it initialize before we actually create the GUI.
# See  http://stackoverflow.com/questions/35803338/python-crashes-after-tkinter-and-matplotlib-pyplot-are-imported
from Tkinter import *
root = Tk()

import cv2      # openCV
import numpy    # needed for openCV
import sys      # so that we can exit()

# Project deprendencies
from blob import Blob
from data import Data
from socket_handler import SocketHandler
from utility import *
from gui import App, Button


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
    faceClassifier = None
    helpTrackbar = "help?"
    startQuitTrackbar = "quit"
    helpOpen = False
    sWindow = "start"
    hWindow = "help window"
    helpImage = "startupHelp.png"
    server_socket = None
    LOOP_ACTIVE = True


    def __init__(self, autostart=False, cameraindex=0):
        """
        Creates a new window so that the user can set the camera index to use, and waits
        until the user drags the start trackbar to 1, starting the rest of the program.
        @param autostart: if false, displays the start / camera index chooser upon startup
        @param cameraindex: initial value of the camera index
        @return: none
        """
        # self.openingPanel = OpenPanel(root)
        # self.default_width = 320
        # self.default_height = 340
        # self.ratio = 1
        # self.frame_width = int(self.default_width * self.ratio)
        # self.frame_height = int(self.default_height * self.ratio)
        # self.root.geometry("%dx%d" % (self.frame_width, self.frame_height))

        self.startButton = Button(root, text="Start", command=self.start)
        self.quitButton = Button(root, text="Quit")
        self.helpButton = Button(root, text = "Help")
        self.cameraLabel = Label(root, text= "Camera Index")
        self.cameraZero = Button(root, text="0")
        self.cameraOne = Button(root, text = "1")
        self.cameraTwo = Button (root, text = "2")

        self.v = StringVar()
        self.cameraInput = Entry(root, textvariable=self.v)
        self.cameraInput.grid(row = 4, column = 1)

        self.v.set("0")


        self.startButton.grid(row=0, column=0)
        self.quitButton.grid(row=2, column=0)
        self.helpButton.grid(row = 3, column=0)
        self.cameraLabel.grid(row = 4, column = 0)
        # self.cameraZero.grid(row = 4, column = 1)
        # self.cameraOne.grid(row = 4, column = 2)
        # self.cameraTwo.grid(row = 4, column =3)

        # Set the initial camera index.
        self.cameraIndex = cameraindex

        # If autostart is True, skip directly to creation of the main GUI.
        if autostart:
            self.startMainServer(self.cameraIndex)
            return


        # Creates the window and gives it a size (otherwise, its width and height is 0).
        cv2.namedWindow(self.sWindow, flags=cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.sWindow, 200, 200)

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
        # cv2.waitKey(1000000)

        while self.LOOP_ACTIVE:
            root.update();

    def start(self):
        self.LOOP_ACTIVE = False
        s = self.v.get()
        print "hi " + s
        self.startMainServer(0)

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

        # Convert the image to grayscale so that opencv can search for faces.
        grayImage = cv2.cvtColor(self.data.video, cv2.COLOR_BGR2GRAY)

        # Look for faces at all scales (otherwise, would look for a certain size face)
        # Edit the raw data into instances of Blob (and put them into data.faceList).
        rawFaceList = self.faceClassifier.detectMultiScale(grayImage)
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
        self.gui = App(root, self.reduce_call_back)

    def startMainServer(self, cameraIndex):
        """
        Start the main program (sensing motion and sending it to clients).
        @param cameraIndex: which camera to connect to.
        @return: none
        """
        self.cameraIndex = cameraIndex
        self.data = Data(self.cameraIndex)
        # Initialize the SocketHandler, which will create the server socket.
        self.server_socket = SocketHandler()
        # Create the GUI to display video feed, motion, and settings.
        self.createGUI()

        # Load the face recognition file into opencv.
        faceType = resource_path("haarcascade_frontalface_alt.xml")
        self.faceClassifier = cv2.CascadeClassifier()
        self.faceClassifier.load(faceType)

        # Start the continuous loop that will run the rest of the program.
        self.run()

    def decideCameraTrackbars(self,x):
        """
        Set the camera index to use, display a help menu when requested, and start
        the rest of the program when prompted.
        @param x: unused parameter; remains for method signature to be correct.
        @return: none
        """
        if cv2.getTrackbarPos(self.cameraChosenTrackbar, self.sWindow) == 1:
            # The start trackbar has been dragged to 1; store the camera index and start the program.
            cameraIndex = cv2.getTrackbarPos(self.cameraTrackbar, self.sWindow)
            # Close the camera index window.
            cv2.destroyWindow(self.sWindow)
            # Start the main program.
            self.startMainServer(cameraIndex)

        if cv2.getTrackbarPos(self.startQuitTrackbar, self.sWindow) == 1:
            # the quit trackbar has been dragged to 1; quit the program.
            cv2.destroyAllWindows()
            sys.exit()

        if cv2.getTrackbarPos(self.helpTrackbar, self.sWindow) == 1 and not self.helpOpen:
            # Open the help window and display the help image on it.
            cv2.namedWindow(self.hWindow)
            # The image needs to first  be read into opencv, and then displayed.
            image = cv2.imread(resource_path(self.helpImage))
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
            self.gui.update()

            # Get the message string, encoding all the relevant interest area and blob data.
            message = self.data.createInformationString()

            # Have the socket check for new incoming connections. Since we don't know how
            # many clients we'll have, or when they'll connect, we check each time. Normally
            # this call would block until it found an incoming connection, but the SocketHandler
            # sets the socket to be non-blocking.
            # Once any new clients have been accepted, send all of the clients the message string.
            self.server_socket.checkIncomingConnections()
            self.server_socket.sendInformation(message)

    def reduce_call_back(self):
        print "pressed reduce"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sense motion and relay information to client applications')
    # If the autostart flag is present, we do not display the camera index choice window.
    parser.add_argument('--autostart', help='Whether to display the start window', action='store_true', default=False)
    # We can also optionally take a camera index from the command line.
    parser.add_argument('-i', '--cameraindex', help='Which camera input to connect to', type=int, default=0)
    args = parser.parse_args()
    # Starts the program.
    Server(autostart=args.autostart, cameraindex=args.cameraindex)
