package event;

import java.util.EventListener;

/** 
 * An interface for registering to listen to CVEvents. 
 * See also CVManager.
*/
public interface CVEventListener extends EventListener  { 
	/** Invoked when shells are detected **/
	public void shellsArrived(CVEvent shellEvt);

	/** Invoked when faces are detected **/
	public void facesArrived(CVEvent faceEvt);

	/** Invoked when any blobs are detected (includes both shells and faces) **/	
	public void blobsArrived(CVEvent blobEvt);
}
