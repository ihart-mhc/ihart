package ihart.event;

import java.util.EventListener;

/** 
 * An interface for registering to listen to CVEvents. 
 * See also CVManager. 
 * @author Kalia Her April 16, 2010
 * @author Felicia Cordeiro 1-17-11
*/
public interface CVEventListener extends EventListener 
{ 
	/** Invoked when holes are detected **/
	public void holesArrived(CVEvent hoEvt); 
	/** Invoked when shells are detected **/
	public void shellsArrived(CVEvent shEvt);
	/** Invoked when faces are detected **/
	public void facesArrived(CVEvent faEvt);
	/** Invoked when any blobs are detected (includes holes, shells and faces) **/	
	public void blobsArrived(CVEvent blobEvt);
}
