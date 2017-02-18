package event;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.EventObject;
import java.util.List;

/**
 * CVEvent extends the Event class as a new type of listener which listens for
 * the information transmitted by the server and creates a user event
 * 
 * @author Cleo Schneider modified by Kalia Her April 16, 2010
 * @author Felicia Cordeiro 1-18-11
 **/

public class CVEvent extends EventObject {
	/**
	 * Fields
	 */
	private CVEventData eventData;
	private EVENT_TYPE type;
	private boolean isResuming;

	// Constants for the different types of blobs.
	public enum EVENT_TYPE {
		SHELL, FACE, ALL_BLOBS
	};

	/**
	 * Constructor that stores all the information about the event
	 *
	 * @param type
	 *            The type of the event
	 * @param cvData
	 *            The event data involved in the event
	 * @param isResuming
	 *            Whether or not the event is resuming
	 *
	 **/
	public CVEvent(EVENT_TYPE type, CVEventData cvData, boolean isResuming) {
		super(cvData);
		this.type = type;
		this.eventData = cvData;
		this.isResuming = isResuming;

	}

	/**
	 * Override the toString function to provide specific functionality for the
	 * CVEvent
	 **/
	public String toString() {
		// TODO: This isn't really... useful?
		return ("Type = " + type + "\n" + eventData.toString());
	}
	
	/**
	 * TODO
	 * @return
	 */
	public int getNumRegionsOfInterest() {
		return eventData.getNumRegionsOfInterest();
	}

	/**
	* Gets the number of blobs
	* @return The number of blobs associated with this type of event
	**/
	public int getTotalNumBlobs(){
		return eventData.getTotalNumBlobs(type);
	}
	
	/**
	 * TODO
	 * @param regionOfInterest
	 * @return
	 */
	public int getNumBlobsInRegion(int regionOfInterest) {
		return eventData.getNumBlobsInRegion(type, regionOfInterest);
	}
	
	/**
	 * TODO
	 * @return
	 */
	public List<Blob> getAllBlobs() {
		return eventData.getAllBlobs(type);
	}
	
	/**
	 * TODO
	 * @param regionOfInterest
	 * @return
	 */
	public List<Blob> getBlobsInRegion(int regionOfInterest) {
		return eventData.getBlobsInRegion(type, regionOfInterest);
	}

	/**
	 * Gets whether or not the event is resuming
	 * 
	 * @return Whether or not the event is resuming
	 *
	 **/
	public boolean isResuming() {
		return isResuming;
	}

	/**
	 * Gets the type of the blob
	 * 
	 * @return The type of the blob as an int. 0 is shell, 1 is hole, 2 is face.
	 **/
	public CVEvent.EVENT_TYPE getType() {
		return type;
	}

}
