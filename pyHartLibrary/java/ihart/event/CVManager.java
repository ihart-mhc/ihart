package ihart.event;

import java.net.*;
import java.util.Vector;
import java.io.*;
import javax.swing.event.EventListenerList;

/**
 * CVManager is a event dispatcher that uses a socket's dataHandler to
 * alert the user of new input
 * @author Cleo Schneider modified by Kalia Her April 16, 2010
 * @author Felicia Cordeiro 1-18-11
 *
 **/

public class CVManager {
	/**
	 * Fields
	 */
	private String hostname = "localhost";
	private int port;

	protected EventListenerList listenerList = new EventListenerList(); 

	// private boolean resumeEvent;
	private int regionOfInterest;
	
	/**
	* The constructor sets up the socket with the given hostName, port, default roi, then
	* connects and sets up listeners
	* on data received dispatch a new CVEvent passing the string
	* received by the dataHandler
	**/
	public CVManager(String hostname, int port )  {
		this( hostname, port, 0 );
	}
	
	/**
	* The constructor sets up the socket with the given hostName, port, roi, then
	* connects and sets up listeners
	* on data received dispatch a new CVEvent passing the string
	* received by the dataHandler
	**/
	public CVManager(String hostname, int port, int roi)  {
		// CVManager.hostname = hostname;
		this.hostname = hostname;
		this.port = port;
		start();
	}
	
	/**
	 * Creates a thread that runs the dataHandler for the port
	 */
	private void start(){
		new Thread(new Runnable() {	         
			public void run() {
				dataHandler(port);
			}
		}).start();
	}
	
	/**
	 * Add a listener to the Event Listener List 
	 * @param listener The listener to be added to the list
	 */
	public void addCVEventListener(CVEventListener listener) { 
		listenerList.add(CVEventListener.class, listener); 
	} 

	/**
	 * Remove a listener to the Event Listener List
	 * @param listener The listener to be removed from the list
	 */
	public void removeCVEventListener(CVEventListener listener) { 
		listenerList.remove(CVEventListener.class, listener); 
	}

	
	/**
	 * Parse the data from the server,store the data, and dispatch the appropriate events.
	 * @param The port to connect to
	 */
	public void dataHandler(int port) {	
		//the string of data from the server
		String fromServer;
		
		//the vector for all of the event  data
		Vector<Vector<Blob>> eventData= new Vector<Vector<Blob>>(0,1);	
		
		//the vectors for each individual type
		Vector<Blob> shellData=new Vector<Blob>(0,1);
		Vector<Blob> holeData=new Vector<Blob>(0,1);
		Vector<Blob> faceData=new Vector<Blob>(0,1);
		
		Socket mySocket = null;
		PrintWriter out = null;
		BufferedReader in = null;

		try {
			//connect to the server with host name "localhost" on port 5204
			mySocket = new Socket("localhost", port);
			out = new PrintWriter(mySocket.getOutputStream(), true);
			in = new BufferedReader(new InputStreamReader(mySocket.getInputStream(),"UTF-8"));
			System.out.println("Found localhost");

			while ((fromServer = in.readLine()) != null) {
				try
				{
					boolean isResuming = false;		//is resume is used to simulate a click event
			
					int numHoles=0;
					int numShells=0;
					int numFaces=0;
					int numWords=0;
					 					
					//if the resume character is found at the beginning of the string set is resuming to true
					if(fromServer.substring(0,2).trim().equals("R")){
						isResuming = true;
						//after slice the character off
						fromServer = fromServer.substring(1);
					}

					int currentInd = fromServer.indexOf(":");
					int numBlobs =  (int) Double.parseDouble(fromServer.substring(0, currentInd));
//					getNumBlobs(fromServer, currentInd);

					for (int i = 0; i < numBlobs; i++){
						//creates a blob object based on the information it gets from the server
						Blob blob=parseEventDataToBlob(fromServer, currentInd);
						
						//get the blobs type
						String blobType=blob.getType();
						//depending on the blobs type, add the blob to the correct array
						if(blobType.equals(CVEvent.SHELL)){
							numShells++;
							shellData.add(blob);
						}
						else if(blobType.equals(CVEvent.HOLE)){
							numHoles++;
							holeData.add(blob);
						}
						else if(blobType.equals(CVEvent.FACE)){
							numFaces++;
							faceData.add(blob);
						}
						
						currentInd = fromServer.indexOf(";", currentInd)+1;
						
					}
					//add each type's data to the overall eventData vector
					eventData.add(shellData);
					eventData.add(holeData);
					eventData.add(faceData);
					
					//dispatch the events
					eventDispatcher(numShells,numHoles,numFaces,numWords,numBlobs,eventData,isResuming);
					
					//empty the data from the last events that were dispatched
					shellData.removeAllElements();
					holeData.removeAllElements();
					faceData.removeAllElements();
					eventData.removeAllElements();
					
				}	
				catch ( StringIndexOutOfBoundsException e ){
					System.out.println( "ERROR!!!!!!!!!!!!!!! out of bounds" );
				}
				catch ( NumberFormatException e ){
					System.out.println( "ERROR!!!!!!!!!!!!!!! number format" );
				}
			}
			
			out.close();
			in.close();
			mySocket.close();
		} catch (UnknownHostException e) {
			System.err.println("Don't know about host: localhost.");
			System.out.println("Can't find localhost");
			System.exit(1);
		} catch (IOException e) {
			System.err.println("Couldn't get I/O for the connection to: localhost on port#:");
			//undecided whether to have the system exit if only one of the connections is unsuccessful
			//System.exit(1);
			
		}
	
	}
	
	/**
	 * Checks the number of each type of blob and dispatches the appropriate events.
	 * If there is at least one of a type of blob, that type of event is dispatched.
	 * If there is at least one blob, then allBlob event type is dispatched
	 * @param numShells The number of shells in the event
	 * @param numHoles The number of holes in the event
	 * @param numFaces The number of faces in the event
	 * @param numWords The number of words in the event
	 * @param numBlobs The number of blobs in the event
 	 * @param eventData The event data
	 * @param resumeEvent A boolean stating whether the event was a resume event of not
	 */
	
	public void eventDispatcher(int numShells, int numHoles, int numFaces,int numWords, int numBlobs, Vector<Vector<Blob>> eventData, boolean resumeEvent){
		CVEventData cvEventData = new CVEventData( eventData,numBlobs, numShells, numHoles, numFaces,numWords );
		
		if(numShells > 0){
			dispatchEvent(new CVEvent(CVEvent.SHELL, cvEventData,resumeEvent));
		}
		if(numHoles > 0){
			dispatchEvent(new CVEvent(CVEvent.HOLE, cvEventData,resumeEvent));
		}
		if(numFaces>0){
			dispatchEvent(new CVEvent(CVEvent.FACE, cvEventData,resumeEvent));
		}
		if(numBlobs>0) {
			dispatchEvent(new CVEvent(CVEvent.ALL_BLOBS, cvEventData,resumeEvent));
		}
	}
	
	/**
	 * Each listener occupies two elements - 
	 * the first is the listener class and the second is the listener instance 
	 * @param evt The event to dispatch
	 */	
	private void dispatchEvent(CVEvent evt) { 
		Object[] listeners = listenerList.getListenerList(); 
		//each listener is going to be held in two elements
		for (int i=0; i<listeners.length; i+=2) { 
			if (listeners[i]==CVEventListener.class){ 
				if(evt.getType().equals(CVEvent.HOLE)){ 			
					((CVEventListener)listeners[i+1]).holesArrived(evt); 
				}
				else if(evt.getType().equals(CVEvent.SHELL)){
					((CVEventListener)listeners[i+1]).shellsArrived(evt);
				}
				else if(evt.getType().equals(CVEvent.FACE)){
					((CVEventListener)listeners[i+1]).facesArrived(evt);
				}	
				else if(evt.getType().equals(CVEvent.ALL_BLOBS)){
					((CVEventListener)listeners[i+1]).blobsArrived(evt);
				}
			}
		}
	}
	
	/**
	* Parses the event data to find the x, y, width, and height of the 
	* current event.
	*
	* @param fromServer The string from the server to be parsed
	*@param currentInd The current index on the string from the server
	* @return  A blob object with the x, y, width, height and word that was parsed
	*
	**/
	private Blob parseEventDataToBlob(String fromServer, int currentInd){
		int xCoord,yCoord,width,height,roi;
		String type;
		
		xCoord=(int) Double.parseDouble(findKeyWordPosition(",","Y",fromServer, currentInd));
		yCoord=(int) Double.parseDouble(findKeyWordPosition("Y","W",fromServer,currentInd));
		width=(int) Double.parseDouble(findKeyWordPosition("W","H",fromServer,currentInd));
		height=(int) Double.parseDouble(findKeyWordPosition("H","T",fromServer,currentInd));
		//the type will come through as an int so here it is being changed to its equivalent string value
		type=CVEvent.getStringType((int) Double.parseDouble(findKeyWordPosition("T","I",fromServer,currentInd)));
		roi = (int) Double.parseDouble(findKeyWordPosition("I",";",fromServer,currentInd));
		return 	new Blob(type,xCoord,yCoord,width,height,roi);
	}
	
	/**
	* Finds the value between the start and end delimiter at the current index
	*
	* @param start The string or character to start looking at
	* @param end The String of character to end looking at
	* @param fromSever The string from the server to be searched
	* 
	*
	**/
	private String findKeyWordPosition(String start, String end, String fromServer, int currentInd){
		int startIndex= fromServer.indexOf(start, currentInd+1) + 1;
		int endIndex=fromServer.indexOf(end, currentInd+1);
		return fromServer.substring(startIndex,endIndex);
	}
	
}
