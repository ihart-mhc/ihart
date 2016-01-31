/**FireworksCV.as
@author: Barsha Shrestha, Mariam, Nikita

This program reacts to motion and paints elliptical blobs whenever motion is detected

**/

package {
	
	/*next steps
	1. create instrucion screen that goes away on the first movement
	2. have a pop up every 30 seconds or so that gives you a color choice - if you swipe left, then one color shows up, and if you swipe right, another one shows up
	3. add sound
	*/
	import flash.geom.Vector3D;
	import flash.geom.ColorTransform;
	import flash.events.*;
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import ihart.event.*;
	import flash.media.Sound;
	import flash.utils.Timer;
	
	public class PaintingCV extends Sprite{
		
		//set up the socket with localhost, using port 5204
		private var hostName:String = "localhost";
		//private var hostName:String = "192.168.10.1"; //hallway
        private var port:uint = 5204;
		//set up a cvManager to handle our CVEvents
		private var cvManager : CVManager;
		
		private var sound: Sound;
		
		private var redpara: RedPara;
		//create a vector of paintblobs
		private var paintblobs : Vector.<Painting> = new Vector.<Painting>();
		
		
		private var WAIT_TIME: int = 150;
		private var SCREEN_TIME: int = 200;
		private var userActive: Boolean;
		var newScreen: WhiteScreen;
		var timer : Timer;
		var cvTimer : Timer;
		public static var CV_DELAY : int = 500;
		var cvEventsAllowed: Boolean;
		var tick : int;
		var cvtick: int;
		var randomInt: int;
		var beach: Beach;
		var xc:Array;	
		var yc: Array;
		var instructionsscreen:instructionsScreen;

		
		
		
		/**
		* Constructor; just initializes the cvManager and adds an event listener to it.
		*/
		public function PaintingCV() : void {
			
			xc = new Array();
			yc = new Array();
		
			instructionsscreen = new instructionsScreen();
			instructionsscreen.visible = true;
			

			cvManager = new CVManager(hostName, port);
			//cvManager.addEventListener(CVEvent.SHELL, getData);
			sound = new PaintSound;
			userActive = false;
			cvTimer = new Timer( CV_DELAY );
			beach = new Beach();
			
			cvTimer.addEventListener(TimerEvent.TIMER, allowCVEvents );
			cvEventsAllowed=true;
			
			tick=-1;
			cvtick=-1;
			
			randomInt = Math.random()*100;
			addEventListener( Event.ENTER_FRAME, tickFunction );
			addEventListener( Event.ENTER_FRAME, startCVEvent );
			addChild(beach);
			addChild(instructionsscreen);
			
			
				
		}
		
		private function allowCVEvents( e : Event ) : void
		{
			cvEventsAllowed = true;
			
			cvTimer.stop();
			trace("Stop it!!");
		}
		
		public function tickFunction (e : Event) : void {	
			tick++;
			
			if ( tick > WAIT_TIME )
			{
		
				removeEventListener( Event.ENTER_FRAME, tickFunction );

				resetGame();
			}
		}
		
		public function startCVEvent(e: Event): void{
			cvtick++;
			if(cvtick> SCREEN_TIME)
			{
				cvManager.addEventListener(CVEvent.SHELL, getData);
			}
		}
		/**
		* Gets data about a CVEvent and creates blobs based on that data.
		*/
		public function getData (e : CVEvent) : void {
			
			var numBlobs : int = e.getNumBlobs();
			var blobX : Number;
			var blobY : Number;
			fireworkX : Number;
			fireworkY : Number;
			var color : int;
			var shape : int;
			var rot :   Number;
			var currentblob : Painting;
			var footprint: Footprint;
			var currentStroke : testStroke;
			var colorTransform: ColorTransform;
			var i:int; 
			var footprintpresent: Boolean ;
			//var footprintpresent: Boolean ;
		
			i=0;
			blobX = e.getX(0);
			blobY = e.getY(0);
			footprint = new Footprint();
			
			//cvManager.removeEventListener(CVEvent.SHELL, getData);
			
			footprint.x=blobX;
			footprint.y = blobY;
			
			
			
			footprintpresent = false;
			
			while(i<xc.length)
			{ 
			
			if(footprint.x >= (xc[i]-25) && footprint.x <= (xc[i]+25) && footprint.y >= (yc[i]-50) && footprint.y <= (yc[i]+50))  
				
			
			{
				//trace("footprint already there? ", footprintpresent);
				
				footprintpresent = true;
			}
			
			//trace("footprint not there");
			i=i+1;
			
			}
			
			
			
			trace("length of array "+xc.length);
			if(footprintpresent ==false)
			{
				//add coordinates to array
				xc.push(footprint.x);
				yc.push(footprint.y);
				//addChild(footprint);
				addFootprint(blobX, blobY);
			}
			else
			{
				trace(" dont add them prints!");
			}
		
			
	
			tick=0;
			
			

		}
		
		public function addFootprint(xc : int, yc :int ) : void{
			var footprint: Footprint;
			footprint = new Footprint();
			
			footprint.x=xc;
			footprint.y = yc;
			
			addChild(footprint);
			
		}
		
		 private function completeHandler(e:TimerEvent):void {
            trace("TIME'S UP HALLELUJAH!!!");  
			 newScreen = new WhiteScreen();
			addChild(newScreen);
			 timer.stop();
        }
		
		
		public function resetGame():void{
			tick=0;
			newScreen = new WhiteScreen();
			addChild(beach);
			randomInt = Math.random()*100;
			addEventListener( Event.ENTER_FRAME, tickFunction );
			randomInt = Math.random()*100;
			
			xc = new Array();
			yc = new Array();
		}
		
		
		
		
	
		
	
		
		
			
		
	}
	
}
		
		