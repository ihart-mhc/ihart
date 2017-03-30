"""
Models an instance of detected motion or a detected face.
"""

class Blob:
    """
    Stores the starting (leftX, topY) coordinates, width, and height of
    either an area of motion or a face. Also stores the region of interest that
    this blob occurred in.

    leftX: the starting x of the blob.
    topY: the starting y of the blob.
    width: the width of the blob.
    height: the height of the blob.
    roi: the region of interest this blob belongs to.
    blob_type: the blob_type of event this blob represents (FACE or SHELL)
    """

    # Constants defining each possible type of blob.
    FACE = "Face"
    SHELL = "Shell"

    # Instance fields
    leftX = None
    topY = None
    width = None
    height = None
    roi = None
    blob_type = None

    def __init__(self, leftX, topY, width, height, roi, blob_type):
        self.leftX = leftX
        self.topY = topY
        self.width = width
        self.height = height
        self.roi = roi
        self.blob_type = blob_type

    def __str__(self):
        return ("<%s -- x: %.2f; y: %.2f; width: %.2f; height: %.2f; in region %d>"
            % (self.type, self.leftX, self.topY, self.width, self.height, self.roi))

    # Called when printing lists
    __repr__ = __str__
