"""
Models an instance of detected motion or a detected face.
"""

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
        using the given four). To exclude a field, pass in -1 or None.

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
        #    Multiplying self.rightX by increase increases the chances that this evaluates to false.
        # If self.leftX > other.rightX, then self starts after other begins (in terms of x).
        #    Multiplying self.leftX by decrease increases the chances that this evaluates to false.
        if((self.rightX * increase) < other.leftX or (self.leftX * decrease) > other.rightX):
            overlap = False

        # If any of the comparisons are True, then the Blobs do not intersect.
        # If self.bottomY < other.topY, then self ends before other begins (in terms of y).
        #    Multiplying self.bottomY by increase increases the chances that this evaluates to false.
        # If self.topY > other.bottomY, then self starts after other begins (in terms of y).
        #    Multiplying self.topY by decrease increases the chances that this evaluates to false.
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
        xChange = newWidth / float(currentWidth)
        yChange = newHeight / float(currentHeight)

        # The value of x should be in relation to the start of currentArea, not the start
        # of the image from the camera (as it currently is). Subtract currentArea.leftX
        # from x to get rid of the portion outside of currentArea. Then multiply the result
        # by the ratio found for converting from currentWidth to newWidth. The result is
        # a correctly scaled new starting x value.
        x = x - currentArea.leftX
        x *= xChange

        # The value of y should be in relation to the start of currentArea, not the start
        # of the image from the camera (as it currently is). Subtract currentArea.topY
        # from y to get rid of the portion outside of currentArea. Then multiply the result
        # by the ratio found for converting from currentHeight to newHeight. The result is
        # a correctly scaled new starting y value.
        y = y - currentArea.topY
        y *= yChange

        # If we scale the width of the blob and then add it to the newly scaled starting x, we
        # get the scaled ending x of the blob. Since the server sends messages using the starting
        # coordinates and a width and height, finding the scaled width is more efficient than
        # finding the scaled end, and then subtracting the scaled start to find the width.
        # (The same goes for y, and height)
        # w and h are simply the width and height of the Blob, so there is nothing to get rid of.
        # Simply multply them by the xChange and yChange ratios.
        w = w * xChange
        h = h * yChange

        # Return the scaled data.
        return (x,y,w,h)
