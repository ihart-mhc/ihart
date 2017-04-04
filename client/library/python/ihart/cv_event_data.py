"""
Collects information about detected motion and faces.
"""

class CVEventData:
    """
    Stores the assorted faces and motion (shells) sent from the server. They
    can be retrieved together, separately, and by which region of interest they
    are contained in.
    """

    _blobs = []
    _blobsByRegion = []
    _faces = []
    _facesByRegion = []
    _shells = []
    _shellsByRegion = []
    _numRoi = 0

    def __init__(self, facesByRegion, shellsByRegion, numRoi):
        # We use the parameters to construct other objects here, so that actual
        # method calls are speedy.
        self._facesByRegion = facesByRegion
        self._faces = [ b for region in facesByRegion for b in region ] # All faces

        self._shellsByRegion = shellsByRegion
        self._shells = [ b for region in shellsByRegion for b in region ] # All shells

        self._numRoi = numRoi

        self._blobs = list(self._faces)
        self._blobs.extend(self._shells) # All blobs (faces and shells)
        self._blobsByRegion = list(self._facesByRegion) # Blobs by region
        for roi, b in enumerate(self._shellsByRegion):
            self._blobsByRegion[roi].extend(b)


    def getAllBlobs(self):
        """
        @return all blobs (faces and shells)
        """
        return self._blobs

    def getAllFaces(self):
        """
        @return all faces
        """
        return self._faces

    def getAllShells(self):
        """
        @return all shells (motion)
        """
        return self._shells

    def getNumRegionsOfInterest(self):
        """
        @return the number of regions of interest
        """
        return self._numRoi

    def getBlobsInRegion(self, roi):
        """
        @param roi  the region of interest to return blobs for
        @return the blobs in the given region
        """
        return self._blobsByRegion[roi]

    def getFacesInRegion(self, roi):
        """
        @param roi  the region of interest to return faces for
        @return the faces in the given region
        """
        return self._facesByRegion[roi]

    def getShellsInRegion(self, roi):
        """
        @param roi  the region of interest to return shells for
        @return the shells in the given region
        """
        return self._shellsByRegion[roi]


    def __str__(self):
        return "<CVEventData with %d faces and %d shells in %d regions of interest>" % (len(self._faces), len(self._shells), self._numRoi)

    # Called when printing lists
    __repr__ = __str__
