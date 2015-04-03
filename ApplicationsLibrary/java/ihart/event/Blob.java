package ihart.event;

	/**
	* Blob is a simple object which provides
	* getters and setters and allows the user the ability
	* to save information for a particular blob
	* @author Cleo Schneider modified by Kalia Her April 16, 2010
	* @author Felicia Cordeiro 1-18-11
	* 
	**/

public class Blob {
	
		
		/**
		* Fields
		**/
		private int xCoor;
		private int yCoor;
		private int bWidth;
		private int bHeight;
		private String type;
		private int roi; // region of interest where this blob occurred
		
		/**
		* Constructor
		* sets all properties for a blob
		*
		* @param eventType The type of the blob
		* @param xCoor The xCoordinate of the center of the blob
		* @param yCoor The yCoordinate of the center of the blob
		* @param bWidth The width of the blob
		* @param bHeight The height of the blob
		*
		**/
		public Blob(String eventType, int xCoor, int yCoor, int bWidth, int bHeight, int roi){ //String
			this.xCoor = xCoor;
			this.yCoor = yCoor;
			this.bWidth = bWidth;
			this.bHeight = bHeight;
			type = eventType;
			this.roi = roi;
		}
		
		/**
		* Returns the xCoor for the center of the blob
		* @return The xCoor for the center of the blob as an int
		**/
		public int getX(){
			return xCoor;
		}
		
		/**
		* Returns the yCoor for the center of the blob
		* @return The yCoor for the center of the blob as an int
		**/
		public int getY(){
			return yCoor;
		}
		
		/**
		* Returns the width of the blob
		* @return The width of the blob as an int
		**/
		public int getWidth(){
			return bWidth;
		}
		
		/**
		* Returns the height of the blob
		* @return The height of the blob as an int
		**/
		public int getHeight(){
			return bHeight;
		}
				
		/**
		* Returns the type of the blob
		* @return The type of the blob as a String
		**/
		public String getType(){ 
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
