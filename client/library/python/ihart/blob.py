"""
Models an instance of detected motion or a detected face.
"""

class Blob:
    """
    Stores the starting (leftX, topY) coordinates, width, and height of
    either an area of motion or a face. Also stores the region of interest that
    this blob occurred in.
    """

    # Constants defining each possible type of blob.
    FACE = "Face"
    SHELL = "Shell"

    def __init__(self, leftX, topY, width, height, roi, type):
        """
        Initializes all instance fields of Blob.

        @param leftX: the starting x of the blob.
        @param topY: the starting y of the blob.
        @param width: the width of the blob.
        @param height: the height of the blob.
        @param roi: the region of interest this blob belongs to.
        @param type: the type of event this blob represents (FACE or SHELL)
        @return: none
        """
        self.leftX = leftX
        self.topY = topY
        self.width = width
        self.height = height
        self.roi = roi
        self.type = type

    def __str__(self):
        return ("<%s -- x: %.2f; y: %.2f; width: %.2f; height: %.2f; in region %d>"
            % (self.type, self.leftX, self.topY, self.width, self.height, self.roi))

    # Called when printing lists
    __repr__ = __str__
