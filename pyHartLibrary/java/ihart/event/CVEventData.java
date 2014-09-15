package ihart.event;

import java.util.Vector;

	/**
	* CVEventData holds all data necessary for a blob event.
	* This class saves all the information from the blob event into a vector
	* @author Cleo Schneider modified by Kalia her April 16, 2010
	* @author Felicia Cordeiro 1-7-11
	**/

public class CVEventData {

		/**
		 * FIELDS
		 */
		private Vector<Vector<Blob>> eventData;
		private Blob blob;	
		private int numBlobs, numShells, numHoles, numFaces, numWords;
		private int[] numTypes;

		/**
		 * The constructor for CVEventData
		 * @param eventData The event data as a multidimensional vector of blobs
		 */
		public CVEventData(Vector<Vector<Blob>> eventData, int numBlobs, int numShells, int numHoles, int numFaces, int numWords){
			this.eventData = eventData;
			this.numBlobs=numBlobs;
			this.numShells=numShells;
			this.numHoles=numHoles;
			this.numFaces=numFaces;
			this.numWords=numWords;
			numTypes=new int[]{numShells,numHoles,numFaces,numWords};
		}
				
		/**
		* Finds the blob of the specified type and with the specified index and returns its x-coordinate
		* 
		* @param eventType The type of event at a String
		* @param index The index of the blob we are looking for
		*
		* @return The xCoor of the center of the blob as type Number
		**/
		public int getX(String eventType, int index){
			blob=getBlob(eventType,index);
			return blob.getX();
		}
		
		/** 
		* Finds the blob of the specified type and with the specified index and returns its y-coordinate
		* 
		* @param eventType The type of event at a String
		* @param index The index of the blob we are looking for
		*
		* @return The yCoor of the center of the blob as type Number
		**/
		public int getY(String eventType, int index){
			blob=getBlob(eventType,index);
			return blob.getY();
		}
		
		/**
		* Finds the blob of the specified type and with the specified index and returns its width
		* 
		* @param eventType The type of event at a String
		* @param index The index of the blob we are looking for
		*
		* @return The width of the blob as type Number
		**/
		public int getWidth(String eventType, int index){
			blob=getBlob(eventType,index);
			return blob.getWidth();
		}
		
		/**
		* Finds the blob of the specified type and with the specified index and returns its height
		* 
		* @param eventType The type of event at a String
		* @param index The index of the blob we are looking for
		*
		* @return The height of the blob as type Number
		**/
		public int getHeight(String eventType, int index){
			blob=getBlob(eventType,index);
			return blob.getHeight();
		}
		
		/**
		* Gets the number of blobs
		* @return The total number of blobs as an integer
		**/
		public int getNumBlobs(){
			return getNum(CVEvent.ALL_BLOBS);
		}
		
		/**
		* Gets the number of blobs of a specified type
		* 
		* @param eventType The type that we are getting the number of blobs of.
		*
		* @return The number of blobs of the specified eventType 
		**/
		public int getNum( String eventType){ //String eventType
			
			if(eventType.equals(CVEvent.ALL_BLOBS)){
				return numBlobs;
			}
			
			else if (eventType.equals(CVEvent.SHELL) || eventType.equals(CVEvent.HOLE) || eventType.equals(CVEvent.FACE) ){
				return numTypes[CVEvent.getIntType(eventType)];
			}

			return -1;
			
		}
		
		/**
		* Gets the blob at the specified index of the specified event type
		*
		* @param index The index of the blob to get
		* @param eventType The type of the event
		* @return The blob that holds all information pertinent to the blob at the specified index
		**/
		public Blob getBlob(String eventType, int index){ 

			if(eventType.equals(CVEvent.ALL_BLOBS) && index < numBlobs){
				if(index >= (numShells)){
					if(index >= numShells + numHoles){
						if(index>=numShells+numHoles+numFaces){
							return eventData.get(3).get(index - numShells - numHoles-numFaces);
						}
						else{
							return eventData.get(2).get(index - numShells - numHoles);
						}
					}
					else{
						return eventData.get(1).get(index - numShells);
					}
				}
				else{
					return eventData.get(0).get(index);
				}
			}
			
			else if(eventType.equals(CVEvent.SHELL) || eventType.equals(CVEvent.HOLE) || eventType.equals(CVEvent.FACE) ){
				return eventData.get(CVEvent.getIntType(eventType)).get(index);
			}
			
			return null;
		}
}
