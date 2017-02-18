package ihart;

import ihart.CVEvent.EVENT_TYPE;

/**
 * Blob is a simple object which provides getters and allows the
 * user to access the information for a particular blob.
 **/
public class Blob {


		/**
		* Fields
		**/
		private double xCoor;
		private double yCoor;
		private double bWidth;
		private double bHeight;
		private CVEvent.EVENT_TYPE type;
		private int roi; // region of interest where this blob occurred

		/**
		* Constructor
		* sets all properties for a blob
		*
		* @param eventType The type of the blob
		* @param xCoor The xCoordinate of the center of the blob
		* @param yCoord The yCoordinate of the center of the blob
		* @param width The width of the blob
		* @param height The height of the blob
		*
		**/
		public Blob(CVEvent.EVENT_TYPE eventType, double xCoor, double yCoord, double width, double height, int roi){
			this.xCoor = xCoor;
			this.yCoor = yCoord;
			this.bWidth = width;
			this.bHeight = height;
			type = eventType;
			this.roi = roi;
		}

		/**
		* Returns the xCoor for the center of the blob
		* @return The xCoor for the center of the blob as an int
		**/
		public double getX(){
			return xCoor;
		}

		/**
		* Returns the yCoor for the center of the blob
		* @return The yCoor for the center of the blob as an int
		**/
		public double getY(){
			return yCoor;
		}

		/**
		* Returns the width of the blob
		* @return The width of the blob as an int
		**/
		public double getWidth(){
			return bWidth;
		}

		/**
		* Returns the height of the blob
		* @return The height of the blob as an int
		**/
		public double getHeight(){
			return bHeight;
		}

		/**
		* Returns the type of the blob
		* @return The type of the blob as a String
		**/
		public EVENT_TYPE getType(){
			return type;
		}

		/**
		* Get region of interest index
		* return roi
		**/
		public int getROI() {
			return roi;
		}
}
