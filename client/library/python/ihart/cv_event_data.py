"""
Collects information about detected motion and faces.
"""

class CVEventData:
    """
    Stores the assorted faces and motion (shells) sent from the server. They
    can be retrieved together, separately, and by which region of interest they
    are contained in.
    """

    blobs = []
    blobsByRegion = []
    faces = []
    facesByRegion = []
    shells = []
    shellsByRegion = []
    numRoi = 0

    def __init__(self, facesByRegion, shellsByRegion, numRoi):
        # We use the parameters to construct other objects here, so that actual
        # method calls are speedy.
        self.facesByRegion = facesByRegion
        self.faces = [ b for region in facesByRegion for b in region ] # All faces

        self.shellsByRegion = shellsByRegion
        self.shells = [ b for region in shellsByRegion for b in region ] # All shells

        self.numRoi = numRoi

        self.blobs = list(self.faces)
        self.blobs.extend(self.shells) # All blobs (faces and shells)
        self.blobsByRegion = list(self.facesByRegion) # Blobs by region
        for roi, b in enumerate(self.shellsByRegion):
            self.blobsByRegion[roi].extend(b)


    def getAllBlobs(self):
        """
        @return all blobs (faces and shells)
        """
        return self.blobs

    def getAllFaces(self):
        """
        @return all faces
        """
        return self.faces

    def getAllShells(self):
        """
        @return all shells (motion)
        """
        return self.shells

    def getNumRegionsOfInterest(self):
        """
        @return the number of regions of interest
        """
        return self.numRoi

    def getBlobsInRegion(self, roi):
        """
        @param roi  the region of interest to return blobs for
        @return the blobs in the given region
        """
        return self.blobsByRegion[roi]

    def getFacesInRegion(self, roi):
        """
        @param roi  the region of interest to return faces for
        @return the faces in the given region
        """
        return self.facesByRegion[roi]

    def getShellsInRegion(self, roi):
        """
        @param roi  the region of interest to return shells for
        @return the shells in the given region
        """
        return self.shellsByRegion[roi]


    def __str__(self):
        return "<CVEventData with %d faces and %d shells>" % (len(self.faces), len(self.shells))
