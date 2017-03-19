"""
A sample iHart application made with kivy.
"""

# Regular python imports
import sys, os

# Import the iHart client library. This path should be the relative path to the
# client/library/python folder in the ihart project.
IHART_PATH = "../../library/python/"

# We normalize the string for this operating system, make it absolute, and append
# it to the python path. DON'T TOUCH THIS. Edit IHART_PATH above.
sys.path.append(os.path.abspath(os.path.normpath(IHART_PATH)) + os.sep)
import ihart

# Kivy imports
import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse
from kivy.uix.widget import Widget


class GUI(Widget):

    CIRCLE_DIAM = 30.0

    def drawCircleFromBlob(self, blob):
        # Draw a circle where the blob is.
        with self.canvas:
            if blob.type == ihart.Blob.FACE:
                Color(1, 1, 0) # Yellow
            else: # ihart.Blob.SHELL
                Color(0, 1, 1) # Blue
            Ellipse(pos=(blob.leftX, blob.topY), size=(self.CIRCLE_DIAM, self.CIRCLE_DIAM))


class SampleIHartApp(App):

    cvManager = None
    cvEventCallback = None
    gui = None

    def build(self):
        # Set up iHart
        self.cvManager = ihart.CVManager()

        # Call processIHartEvents after every frame.
        self.cvEventCallback = Clock.schedule_interval(self.processIHartEvents, 0)

        # GUI
        self.gui = GUI()
        return self.gui

    def processIHartEvents(self, dt):
        """
        Callback for processing iHart events.
        @param dt "delta-time", unused but requred by kivy
        """
        # Get any new events from the server since the last time this method
        # was called.
        eventData = self.cvManager.getNewEvents()

        # eventData can be None, so only get blobs if it exists.
        if eventData:
            blobs = eventData.getAllBlobs()
            print "received", len(blobs), "blob(s) from iHart server"

            # Draw a circle for each blob.
            for blob in blobs:
                self.gui.drawCircleFromBlob(blob)


    def on_stop(self):
        """
        Called when the application has finished running (i.e. the window is
        about to be closed).
        """
        # Close the connection to the server.
        self.cvManager.destroy()


if __name__ == '__main__':
    SampleIHartApp().run()
