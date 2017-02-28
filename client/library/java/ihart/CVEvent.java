package ihart;

import java.util.EventObject;
import java.util.List;

/**
 * CVEvent extends the Event class as a new type of listener which listens for
 * the information transmitted by the server and creates a user event
 **/

@SuppressWarnings("serial")
public class CVEvent extends EventObject {
	/**
	 * Fields
	 */
	private CVEventData eventData;
	private EVENT_TYPE type;

	// Constants for the different types of blobs.
	public enum EVENT_TYPE {
		SHELL, FACE, ALL_BLOBS
	};

	/**
	 * Store all the information about the event.
	 *
	 * @param type
	 *            The type of the event
	 * @param cvData
	 *            The event data involved in the event
	 **/
	public CVEvent(EVENT_TYPE type, CVEventData cvData) {
		super(cvData);
		this.type = type;
		this.eventData = cvData;
	}

	@Override
	public String toString() {
		return "Type: " + type;
	}

	/**
	 * @return The number of regions of interest that are currently active and
	 *         associated with this event.
	 */
	public int getNumRegionsOfInterest() {
		return eventData.getNumRegionsOfInterest();
	}

	/**
	 * @return The number of blobs associated with this type of event
	 **/
	public int getTotalNumBlobs() {
		return eventData.getTotalNumBlobs(type);
	}

	/**
	 * Get the number of blobs in a particular region of interest.
	 * 
	 * @param regionOfInterest
	 *            The index of the region of interest. This will throw an
	 *            exception if the region does not exist.
	 * @return The number of blobs in a particular region of interest
	 */
	public int getNumBlobsInRegion(int regionOfInterest) {
		return eventData.getNumBlobsInRegion(type, regionOfInterest);
	}

	/**
	 * @return All of the blobs associated with this event.
	 */
	public List<Blob> getAllBlobs() {
		return eventData.getAllBlobs(type);
	}

	/**
	 * Get the blobs associated with this event that occurred within the given
	 * region of interest.
	 * 
	 * @param regionOfInterest
	 *            The index of the region of interest. This will throw an
	 *            exception if the region does not exist.
	 * @return The blobs that occurred within the given region of interest
	 */
	public List<Blob> getBlobsInRegion(int regionOfInterest) {
		return eventData.getBlobsInRegion(type, regionOfInterest);
	}

	/**
	 * @return The type of the event (SHELL, FACE, or ALL_BLOBS)
	 **/
	public CVEvent.EVENT_TYPE getType() {
		return type;
	}

}
