/**FireworksCV.as
@author Allison DeJordy
CS240 Mini-Project

This program reacts to Hulls by generating Fireworks near the Hull. Each Firework is randomly offset in both the x and y directions and
receives a random color (red, blue, green or purple) and rotation.

**/

package {
	
	import flash.geom.Vector3D;
	import flash.geom.ColorTransform;
	import flash.events.*;
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import ihart.event.*;
	
	public class FireworksCV extends Sprite{
		
		//set up the socket with localhost, using port 5204
		private var hostName:String = "localhost";
		//private var hostName:String = "192.168.10.1"; //hallway
        private var port:uint = 5204;
		//set up a cvManager to handle our CVEvents
		private var cvManager : CVManager;
		//the maximum y offset of the fireworks
		private var yOffsetMax = 75;
		//the maximum x offset of the fireworks
		private var xOffsetMax = 75;
		
		//create a vector of fireworks
		private var fireworks : Vector.<Firework> = new Vector.<Firework>();
		
		/**
		* Constructor; just initializes the cvManager and adds an event listener to it.
		*/
		public function FireworksCV() : void {
			
			cvManager = new CVManager(hostName, port);
			cvManager.addEventListener(CVEvent.SHELL, getData);
			
		}
		
		/**
		* Gets data about a CVEvent and fires fireworks based on that data.
		*/
		public function getData (e : CVEvent) : void {
			trace( "getting data " );
			var numBlobs : int = e.getNumBlobs();
			var blobX : Number;
			var blobY : Number;
			fireworkX : Number;
			fireworkY : Number;
			var color : int;
			var rot : Number;
			var currentFirework : Firework;
			var colorTransform: ColorTransform;
			
			//for every blob there is on the screen
			for (var i : int = 0; i < numBlobs; i++) {
				
				currentFirework = new Firework();
				
				//save the blob's x and y values
				blobX = e.getX(i);
				blobY = e.getY(i);
				
				//generate a random color for the firework
				color = Math.ceil(Math.random() * 4);
				
				//create a new firework with the chosen color by applying a color transform in every case except red
				switch (color) {
					
					case 1:
						break;
						
					case 2:
						colorTransform = currentFirework.transform.colorTransform;
						colorTransform.color = 0x3399FF;
						currentFirework.transform.colorTransform = colorTransform;
						break;
						
					case 3:
						colorTransform = currentFirework.transform.colorTransform;
						colorTransform.color = 0x9933FF;
						currentFirework.transform.colorTransform = colorTransform;
						break;
						
					case 4:
						colorTransform = currentFirework.transform.colorTransform;
						colorTransform.color = 0x00FF33;
						currentFirework.transform.colorTransform = colorTransform;
						break;
						
					default:
						break;
						
				}
				
				//add a random rotation to the firework (between 0 and 60 degrees)
				rot = Math.random() * 60;
				
				currentFirework.rotation = rot;
				
				
				//add the new firework to the scene
				addChild(currentFirework);
				
				//generate the new firework's x and y based on the blob's x and y
				currentFirework.x = generateOffset(blobX, xOffsetMax);
				currentFirework.y = generateOffset(blobY, yOffsetMax);
				
				//add the new firework to the vector
				 fireworks.push(currentFirework);
				
				//remove any old fireworks
				removeOld();
				
			}

		}
		
		/**
		* Removes fireworks that have disappeared from view from the screen and the vector.
		**/
		public function removeOld () : void {
			
			//for every firework in the vector
			for (var i : int = 0; i < fireworks.length; i++) {
				
				//if the reference portion of the firework is not visible
				if (fireworks[i].currentFrame == 30) {
					
					//remove the firework from the screen
					removeChild(fireworks[i]);
					
					//remove the firework from the vector
					fireworks.splice(i, 1);

				}
				
			}
			
		}
		
		/**
		* Generates a random offset for a firework's x or y value.
		**/
		public function generateOffset (initialNum : Number, maxOffset : Number) : Number {
			
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
		
		