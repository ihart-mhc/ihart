package ihart;

import java.util.ArrayList;
import java.util.List;

/**
 * CVEventData holds all data necessary for a blob event. A CVEventData object
 * may be associated with one or more CVEvent objects, since a FACE or SHELL
 * event will also trigger an ALL_BLOBS event.
 **/

public class CVEventData {

	/**
	 * FIELDS
	 */
	// All blobs
	private List<Blob> allEventData;

	// All blobs representing faces in one list
	private List<Blob> allFaceData;

	// Blobs representing faces, separated by region of interest
	private List<ArrayList<Blob>> faceDataByRegion;

	// All blobs representing shells in one list
	private List<Blob> allShellData;

	// Blobs representing shells, separated by region of interest
	private List<ArrayList<Blob>> shellDataByRegion;

	private int numRegionsOfInterest;

	/**
	 * The constructor for CVEventData.
	 */
	public CVEventData(List<ArrayList<Blob>> faceDataByRegion, List<ArrayList<Blob>> shellDataByRegion,
			int numRegionsOfInterest) {
		this.shellDataByRegion = shellDataByRegion;
		this.faceDataByRegion = faceDataByRegion;

		// allFaceData and allShellData are collected from faceData and
		// shellData. They're created here instead of whenever methods are
		// called in order to save time.
		allFaceData = new ArrayList<Blob>();
		for (ArrayList<Blob> blobs : faceDataByRegion) {
			allFaceData.addAll(blobs);
		}

		allShellData = new ArrayList<Blob>();
		for (ArrayList<Blob> blobs : shellDataByRegion) {
			allShellData.addAll(blobs);
		}

		// Event data is a list of all blob types, maintained for convenience.
		allEventData = new ArrayList<Blob>(allFaceData);
		allEventData.addAll(allShellData);

		this.numRegionsOfInterest = numRegionsOfInterest;
	}

	/**
	 * @return The number of regions/areas of interest
	 */
	public int getNumRegionsOfInterest() {
		return numRegionsOfInterest;
	}

	/**
	 * Get the total number of blobs.
	 * 
	 * @param type
	 *            The type of event to return the number of blobs for
	 * @return The total number of blobs
	 **/
	public int getTotalNumBlobs(CVEvent.EVENT_TYPE type) {
		switch (type) {
		case FACE:
			return allFaceData.size();
		case SHELL:
			return allShellData.size();
		case ALL_BLOBS: // Fall through
		default:
			return allEventData.size();

		}
	}

	/**
	 * Get the number of blobs in a particular region of interest.
	 * 
	 * @param type
	 *            The type of event to return the number of blobs for
	 * @param regionOfInterest
	 *            The index of the region of interest. This will throw an
	 *            exception if the region does not exist.
	 * @return The number of blobs in a particular region of interest
	 */
	public int getNumBlobsInRegion(CVEvent.EVENT_TYPE type, int regionOfInterest) {
		switch (type) {
		case FACE:
			return faceDataByRegion.get(regionOfInterest).size();
		case SHELL:
			return shellDataByRegion.get(regionOfInterest).size();
		case ALL_BLOBS: // Fall through
		default:
			// We want both the faces and the shells.
			return faceDataByRegion.get(regionOfInterest).size() + shellDataByRegion.get(regionOfInterest).size();

		}
	}

	/**
	 * Get all of the blobs associated with this event.
	 * 
	 * @param type
	 *            The type of event to return the blobs for
	 * @return All blobs.
	 */
	public List<Blob> getAllBlobs(CVEvent.EVENT_TYPE type) {
		switch (type) {
		case FACE:
			return allFaceData;
		case SHELL:
			return allShellData;
		case ALL_BLOBS: // Fall through
		default:
			// eventData is the overall list of all blobs in this event.
			return allEventData;

		}
	}

	/**
	 * Get the blobs associated with this event that occurred within the given
	 * region of interest.
	 * 
	 * @param type
	 *            The type of event to return the blobs for
	 * @param regionOfInterest
	 *            The index of the region of interest. This will throw an
	 *            exception if the region does not exist.
	 * @return The blobs of a particular type that occurred within the given
	 *         region of interest
	 */
	public List<Blob> getBlobsInRegion(CVEvent.EVENT_TYPE type, int regionOfInterest) {
		switch (type) {
		case FACE:
			return faceDataByRegion.get(regionOfInterest);
		case SHELL:
			return shellDataByRegion.get(regionOfInterest);
		case ALL_BLOBS: // Fall through
		default:
			// We want both the faces and the shells.
			List<Blob> blobs = new ArrayList<Blob>(faceDataByRegion.get(regionOfInterest));
			blobs.addAll(shellDataByRegion.get(regionOfInterest));
			return blobs;

		}
	}
}
