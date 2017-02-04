"""
Represents a rectangle on the screen; if mostion/faces occur within that rectangle,
the server passes that information on to the clients.
"""

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
