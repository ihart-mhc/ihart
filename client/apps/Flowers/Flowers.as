/**
Flowers.as
@author Pavlina Lejskova '15
CS295 iHart Independent Study Spring '14

This program reacts to Hulls by generating flowers near the Hull.
Each flower is randomly offset in both the x and y directions and
receives a random rotation.
**/

package {
	
	import flash.geom.Vector3D;
	import flash.events.*;
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import ihart.event.*;
	
	public class Flowers extends Sprite{
		
		//set up the socket with localhost, using port 5204
		private var hostName:String = "localhost";
	  	//private var hostName:String = "192.168.10.1"; //hallway
        private var port:uint = 5204;
		
		//set up a cvManager to handle our CVEvents
		private var cvManager : CVManager;
		
		//the maximum x and y offset of the flowers
		private var yOffsetMax = 50;
		private var xOffsetMax = 50;
		
		//create a vector of flowers
		private var flowers: Vector.<Bud> = new Vector.<Bud>();
		
		/**
		* Constructor initializes the cvManager and adds an event listener to it.
		*/
		public function Flowers() : void {
			cvManager = new CVManager(hostName, port);
			cvManager.addEventListener(CVEvent.SHELL, getData);
		}
		
		/**
		* Gets data about a CVEvent and creates flowers based on that data.
		*/
		public function getData (e : CVEvent) : void {
			
			trace( "Acquiring data... " );
			var numBlobs : int = e.getNumBlobs();
			var blobX : Number;
			var blobY : Number;
			var rot : Number;
			var currentFlower : Bud;
			
			//for every blob there is on the screen
			for (var i : int = 0; i < numBlobs; i++) {
				
				currentFlower = new Bud();
				
				//save the blob's x and y values
				blobX = e.getX(i);
				blobY = e.getY(i);
				
				//add a random rotation to the flower (between 0 and 60 degrees)
				rot = Math.random() * 60;
				currentFlower.rotation = rot;
				
				//add the new flower to the scene
				addChild(currentFlower);
				
				//generate the new flower's x and y based on the blob's x and y
				currentFlower.x = generateOffset(blobX, xOffsetMax);
				currentFlower.y = generateOffset(blobY, yOffsetMax);
				
				//add the new flower to the vector
				flowers.push(currentFlower);
				
				//remove any old flowers
				removeOld();
			}
		}
		
		/**
		* Removes flowers that have disappeared from view from the screen and the vector.
		**/
		public function removeOld () : void {
			
			//for every flower in the vector
			for (var i : int = 0; i < flowers.length; i++) {
				
				//if the reference portion of the flower is not visible
				if (flowers[i].currentFrame == 20) {
					
					//remove the flower from the screen
					removeChild(flowers[i]);
					
					//remove the flower from the vector
					flowers.splice(i, 1);
				}
			}
		}
		
		/**
		* Generates a random offset for a flower's x or y value.
		**/
		public function generateOffset (initialNum: Number, maxOffset: Number): Number {
			
			//set the amount of offset randomly
			var offset : Number = Math.random() * maxOffset;
			
			//set the sign of the offset (0 is negative, 1 is positive)
			var sign : int = Math.floor(Math.random() * 2);
			
			if (sign == 0) {
				return initialNum - offset;
			}
			
			return initialNum + offset;
		}
		
	}
}
		
		