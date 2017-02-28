import java.util.List;

import ihart.Blob;
import ihart.CVEvent;
import ihart.CVEventListener;
import ihart.CVManager;

/**
 * Listens for CVEVents and prints out the type of each event, and the x, y,
 * width, and height for each blob associated with the event.
 **/
public class PrintlnProgram implements CVEventListener {

	CVManager cvmanager;

	/**
	 * Listens for shells and prints the information (x, y, width, height, type)
	 * for each event
	 * 
	 * @param shEvt
	 *            the CVEvent for the shell
	 */
	public void shellsArrived(CVEvent shEvt) {
		System.out.println("shells have arrived!");

		// Print all of the information for the event.
		 printEventInformation(shEvt);

		// Print the information, grouped by region of interest.
		// printEventInformationByRegion(shEvt);
	}

	/**
	 * Listens for faces and prints the information (x, y, width, height, type)
	 * for each event
	 * 
	 * @param faEvt
	 *            the CVEvent for the face
	 */
	public void facesArrived(CVEvent faEvt) {
		System.out.println("faces have arrived!");

		// Print all of the information for the event.
		 printEventInformation(faEvt);

		// Print the information, grouped by region of interest.
		// printEventInformationByRegion(faEvt);
	}

	/**
	 * Listens for blobs, which include shells and faces. Since the program also
	 * listens for each event individually, the content in this method is
	 * intentionally commented out.
	 * 
	 * @param blobEvt
	 *            the CVEvent for the blob
	 */
	public void blobsArrived(CVEvent blobEvt) {
		// a blob alert is sent for shells and faces
		// System.out.println("blobs have arrived!");

		// Print all of the information
		// printEventInformation(blobEvt);
		
		// Print the information, grouped by region of interest.
		// printEventInformationByRegion(blobEvt);
	}

	/**
	 * Prints the information belonging to each CVEvent (x, y, width, height,
	 * type)
	 * 
	 * @param event
	 *            the event to print information from
	 */
	public void printEventInformation(CVEvent event) {
		String output = "Event Type: " + event.getType() + "\n";

		// finds number of associated blobs; adds appropriate statement to
		// output string
		int numBlobs = event.getTotalNumBlobs();
		if (numBlobs == 1) {
			output += "1 blob is associated with this event.\n";
		} else {
			output += numBlobs + " blobs are associated with this event.\n";
		}

		// prints x, y, width, and height for each blob associated with the
		// event
		List<Blob> blobs = event.getAllBlobs();
		for (Blob b : blobs) {
			output += b.getType() + ": ";
			output += "{ x = " + b.getX();
			output += ", y = " + b.getY();
			output += ", width = " + b.getWidth();
			output += ", height = " + b.getHeight() + " }\n";
		}

		System.out.println(output);
	}

	/**
	 * Prints the information belonging to each CVEvent (x, y, width, height,
	 * type), grouped by the region of interest each blob occurred in.
	 * 
	 * @param event
	 *            the event to print information from
	 */
	public void printEventInformationByRegion(CVEvent event) {
		String output = "Event Type: " + event.getType() + "\n";

		// finds number of associated blobs; adds appropriate statement to
		// output string
		int numBlobs = event.getTotalNumBlobs();
		if (numBlobs == 1) {
			output += "1 blob is associated with this event.\n";
		} else {
			output += numBlobs + " blobs are associated with this event.\n";
		}

		// Add region of interest information to the output.
		int numRegionsOfInterest = event.getNumRegionsOfInterest();
		if (numRegionsOfInterest == 1) {
			output += "1 region of interest is associated with this event.\n";
		} else {
			output += numRegionsOfInterest + " regions of interest are associated with this event.\n";
		}

		for (int i = 0; i < numRegionsOfInterest; i++) {
			output += "Region " + i + " has " + event.getNumBlobsInRegion(i) + " blob(s).\n";
			List<Blob> blobsInRegion = event.getBlobsInRegion(i);
			for (Blob b : blobsInRegion) {
				output += "\t" + b.getType() + ": ";
				output += "{ x = " + b.getX();
				output += ", y = " + b.getY();
				output += ", width = " + b.getWidth();
				output += ", height = " + b.getHeight() + " }\n";
			}
		}

		System.out.println(output);
	}

	/**
	 * Creates a new instance of PrintlnProgram
	 *
	 * @param args
	 *            none expected
	 **/
	public static void main(String[] args) {
		System.out.println("in main of PrintlnProgram");
		new PrintlnProgram();
	}

	/**
	 * Creates initializes instance of CVManager, subscribes to CVEvents.
	 **/
	public PrintlnProgram() {
		System.out.println("in constructor of PrintlnProgram");
		cvmanager = new CVManager("localhost", 5204);
		cvmanager.addCVEventListener(this);
	}
}
