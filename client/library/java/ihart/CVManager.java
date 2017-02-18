package event;

import java.net.*;
import java.util.ArrayList;
import java.util.List;
import java.io.*;
import javax.json.Json;
import javax.json.JsonArray;
import javax.json.JsonObject;
import javax.json.JsonReader;
import javax.json.JsonValue;
import javax.swing.event.EventListenerList;

/**
 * CVManager is an event dispatcher that uses a socket's dataHandler to alert
 * the user of new events.
 **/

public class CVManager {
	/**
	 * Fields
	 */
	private String hostname = "localhost";
	private int port;

	protected EventListenerList listenerList = new EventListenerList();

	/**
	 * The constructor sets up the socket with the given hostName and port, then
	 * connects and sets up listeners for data received and dispatches
	 * corresponding CVEvents when motion events occur.
	 **/
	public CVManager(String hostname, int port) {
		this.hostname = hostname;
		this.port = port;
		start();
	}

	/**
	 * Create a thread that runs the dataHandler for the port.
	 */
	private void start() {
		new Thread(new Runnable() {
			public void run() {
				dataHandler(port);
			}
		}).start();
	}

	/**
	 * Add a listener to the Event Listener List.
	 * 
	 * @param listener
	 *            The listener to be added to the list
	 */
	public void addCVEventListener(CVEventListener listener) {
		listenerList.add(CVEventListener.class, listener);
	}

	/**
	 * Remove a listener to the Event Listener List.
	 * 
	 * @param listener
	 *            The listener to be removed from the list
	 */
	public void removeCVEventListener(CVEventListener listener) {
		listenerList.remove(CVEventListener.class, listener);
	}

	/**
	 * Parse the data from the server, store the data, and dispatch the
	 * appropriate events.
	 * 
	 * @param The
	 *            port to connect to
	 */
	public void dataHandler(int port) {
		// the string of data from the server
		String fromServer;

		Socket mySocket = null;
		PrintWriter out = null;
		BufferedReader in = null;

		try {
			// connect to the server with host name "localhost" on port 5204
			mySocket = new Socket("localhost", port);
			out = new PrintWriter(mySocket.getOutputStream(), true);
			in = new BufferedReader(new InputStreamReader(mySocket.getInputStream(), "UTF-8"));
			System.out.println("Connected to localhost");

			while ((fromServer = in.readLine()) != null) {
				try {
					boolean isResuming = false; // is resume is used to simulate
												// a click event

					// TODO: I don't think this is included anymore? The flash
					// library has it, though.
					// if the resume character is found at the beginning of the
					// string set is resuming to true
					if (fromServer.substring(0, 2).trim().equals("R")) {
						isResuming = true;
						// after slice the character off
						fromServer = fromServer.substring(1);
					}

					// Remove newline/carriage returns because the JSON parser
					// doesn't like them.
					fromServer = fromServer.replaceAll("\n", "");
					fromServer = fromServer.replaceAll("\0", "");
					fromServer = fromServer.replaceAll("\r", "");

					JsonReader reader = Json.createReader(new StringReader(fromServer));

					// We start with an array of the areas of interest.
					JsonArray areasOfInterest = (JsonArray) (reader.read());
					int numAreasOfInterest = areasOfInterest.size();

					// Lists to hold the data of each type; separated into lists
					// by region of interest. (Eg, all of the faces from the
					// first region of interest would be in faceData.get(0).)
					// This would be typed as List<List<Blob>> but it doesn't
					// compile that way.
					List<ArrayList<Blob>> shellData = new ArrayList<ArrayList<Blob>>(numAreasOfInterest);
					List<ArrayList<Blob>> faceData = new ArrayList<ArrayList<Blob>>(numAreasOfInterest);

					// Whether or not we actually have blob information.
					boolean haveShells = false;
					boolean haveFaces = false;

					// Each are of interest is an object with keys for "Faces"
					// and "Shells". We would use the original JsonArrays, but
					// we need to convert the data into Blob objects.
					for (int i = 0; i < numAreasOfInterest; i++) {
						JsonObject aoi = areasOfInterest.getJsonObject(i);
						ArrayList<Blob> current = new ArrayList<Blob>();

						JsonArray shells = aoi.getJsonArray("Shells");
						shellData.add(current);
						for (JsonValue val : shells) {
							haveShells = true;
							JsonArray shell = (JsonArray) (val);
							current.add(parseEventDataToBlob(shell, i /* roi */, CVEvent.EVENT_TYPE.SHELL));
						}

						JsonArray faces = aoi.getJsonArray("Faces");
						current = new ArrayList<Blob>();
						faceData.add(current);
						for (JsonValue val : faces) {
							haveFaces = true;
							JsonArray face = (JsonArray) (val);
							current.add(parseEventDataToBlob(face, i /* roi */, CVEvent.EVENT_TYPE.FACE));
						}

					}

					// Dispatch the events with the associated data.
					eventDispatcher(faceData, haveFaces, shellData, haveShells, numAreasOfInterest, isResuming);

				} catch (ClassCastException e) {
					System.out.println("Unexpected message format from server: " + e);
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
			System.err.println("Couldn't get I/O for the connection to: " + hostname + " on port " + port);
			// undecided whether to have the system exit if only one of the
			// connections is unsuccessful
			// System.exit(1);

		}

	}

	/**
	 * Checks the number of each type of blob and dispatches the appropriate
	 * events. If there is at least one of a type of blob, that type of event is
	 * dispatched. If there is at least one blob, then allBlob event type is
	 * dispatched
	 * 
	 * @param numShells
	 *            The number of shells in the event
	 * @param numHoles
	 *            The number of holes in the event
	 * @param numFaces
	 *            The number of faces in the event
	 * @param numBlobs
	 *            The number of blobs in the event
	 * @param eventData
	 *            The event data
	 * @param resumeEvent
	 *            A boolean stating whether the event was a resume event of not
	 */
	public void eventDispatcher(List<ArrayList<Blob>> faceData, boolean haveFaces, List<ArrayList<Blob>> shellData,
			boolean haveShells, int numAreasOfInterest, boolean resumeEvent) {
		CVEventData cvEventData = new CVEventData(faceData, shellData, numAreasOfInterest);

		if (haveShells) {
			dispatchEvent(new CVEvent(CVEvent.EVENT_TYPE.SHELL, cvEventData, resumeEvent));
		}
		if (haveFaces) {
			dispatchEvent(new CVEvent(CVEvent.EVENT_TYPE.FACE, cvEventData, resumeEvent));
		}
		// If we have either type of blob (or both), send out a general blob
		// event.
		if (haveShells || haveFaces) {
			dispatchEvent(new CVEvent(CVEvent.EVENT_TYPE.ALL_BLOBS, cvEventData, resumeEvent));
		}
	}

	/**
	 * Each listener occupies two elements - the first is the listener class and
	 * the second is the listener instance
	 * 
	 * @param evt
	 *            The event to dispatch
	 */
	private void dispatchEvent(CVEvent evt) {
		Object[] listeners = listenerList.getListenerList();
		// each listener is going to be held in two elements
		for (int i = 0; i < listeners.length; i += 2) {
			if (listeners[i] == CVEventListener.class) {
				if (evt.getType().equals(CVEvent.EVENT_TYPE.SHELL)) {
					((CVEventListener) listeners[i + 1]).shellsArrived(evt);
				} else if (evt.getType().equals(CVEvent.EVENT_TYPE.FACE)) {
					((CVEventListener) listeners[i + 1]).facesArrived(evt);
				} else if (evt.getType().equals(CVEvent.EVENT_TYPE.ALL_BLOBS)) {
					((CVEventListener) listeners[i + 1]).blobsArrived(evt);
				}
			}
		}
	}

	/**
	 * Parses the event data to find the x, y, width, and height of the current
	 * event.
	 *
	 * @param blobData
	 *            A JsonArray containing the x, y, width, and height of a blob
	 * @param roi
	 *            The region of interest this blob occurred in
	 * @param type
	 *            The type of event (shell or face)
	 * @return A blob object with the x, y, width, and height that was parsed
	 *
	 **/
	private Blob parseEventDataToBlob(JsonArray blobData, int roi, CVEvent.EVENT_TYPE type) {
		// Get the leftX, topY, width, and height from the JSON data.
		double xCoord = blobData.getJsonNumber(0).doubleValue();
		double yCoord = blobData.getJsonNumber(1).doubleValue();
		double width = blobData.getJsonNumber(2).doubleValue();
		double height = blobData.getJsonNumber(3).doubleValue();

		return new Blob(type, xCoord, yCoord, width, height, roi);
	}

}
