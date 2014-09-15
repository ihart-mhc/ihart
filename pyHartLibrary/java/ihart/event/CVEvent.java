package ihart.event;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.EventObject;

/**
	* CVEvent extends the Event class as a new type of listener which listens
	* for the information transmitted by the server and creates a user event
	* @author Cleo Schneider modified by Kalia Her April 16, 2010
	* @author Felicia Cordeiro 1-18-11
	**/

public class CVEvent extends EventObject {
	/**
	 * Fields
	 */
	private CVEventData cvData; 
	private String type; 
	private boolean isResuming;
	
	//Constants for the different types of blobs
	public static final String SHELL = "shell"; 
	public static final String HOLE = "hole";
	public static final String FACE="face";
	public static final String ALL_BLOBS = "all_blobs";
	public static final ArrayList<String> types=new ArrayList<String>(Arrays.asList(SHELL,HOLE,FACE));
	
	/**
	* Constructor that stores all the information about the event
	*
	* @param type The type of the event
	* @param cvData The event data involved in the event
	* @param isResuming Whether or not the event is resuming
	*
	**/	
	public CVEvent (String type, CVEventData cvData, boolean isResuming){	//String type2,
		super(cvData);
		this.type = type;
		this.cvData = cvData;
		this.isResuming=isResuming;
		
	}
	
	/**
	* Takes the type of event as a String for a parameter, and
	* gets the cooresponding type of event as an integer
	*
	* @param type The type of the blob as a String
	*
	* @return The type of event as an int
	**/
	public static int getIntType(String type){
		return types.indexOf(type);
	}
	
	/**
	* Takes the type of event as an integer for a parameter, and
	* gets the cooresponding type of event as a String
	*
	* @param type The type of the blob as an integer
	*
	* @return The type of event as an String
	**/
	public static String getStringType(int type){
		return types.get(type);
	}

	
	/**
	* Override the toString function to provide 
	* specific functionality for the CVEvent
	**/
	public String toString(){
		return ("Type = " + type + cvData.toString());
	}

	/**
	* Gets the xCoor of the center of the blob
	* @return The xCoor of the center of the blob as type Number
	**/
	public int getX(int index){
		return cvData.getX(type, index);
	}
	
	/**
	* Gets the yCoor of the center of the blob
	* @return The yCoor of the center of the blob as type Number
	**/
	public int getY(int index){
		return cvData.getY(type, index);
	}
	
	/**
	* Gets the width of the blob
	* @return The width of the blob as type Number
	**/
	public int getWidth(int index){
		return cvData.getWidth(type, index);
	}
	
	/**
	* Gets the height of the blob
	* @return The height of the blob as type Number
	**/
	public int getHeight(int index){
		return cvData.getHeight(type, index);
	}
	
	/**
	* Gets the number of blobs
	* @return The number of blobs associated with this type of event
	**/
	public int getNumBlobs(){
		return cvData.getNumBlobs();
	}
	
	/**
	* Gets the blob at the specified index
	*
	* @param index The index of the blob to get
	*
	* @return The blob that holds all information pertinent to the blob at the specified index
	**/
	public Blob getBlob(int index){
		return cvData.getBlob(type, index);
	}
	
	/**
	* Gets whether or not the event is resuming
	* @return Whether or not the event is resuming
	*
	**/
	public boolean isResuming(){
		return isResuming;
	}
	
	/**
	* Gets the type of the blob
	* @return The type of the blob as an int. 0 is shell, 1 is hole, 2 is face.
	**/
	public String getType(){
		return type;
	}
	
}
	
	
	