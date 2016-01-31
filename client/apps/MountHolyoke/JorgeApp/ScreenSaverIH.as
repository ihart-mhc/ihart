package  {
	
	//import statements 
	import flash.events.*;
	import flash.display.MovieClip;
	import ihart.event.*;
	import flash.utils.Timer;
    import flash.events.TimerEvent;
	//a timer to time when to refresh display 
	
	
	public class ScreenSaverIH extends MovieClip{
		
		//set up the socket with localhost, using port 5204
		private var hostName:String = "localhost";
		//private var hostName:String = "192.168.10.1"; //hallway
        private var port:uint = 5204;
		//set up a cvManager to handle our CVEvents
		private var cvManager : CVManager;
		
		//screensaver 
		private var screenSaver: ScreenSaver = new ScreenSaver();
		
		//timer 
		private var starTimer:Timer = new Timer(15000,1);
	       //new cvManager 
		cvManager = new CVManager(hostName, port);
			

		public function ScreenSaverIH() {
			// constructor code
			
			//make sure the cvManager is checking for motion 
			cvManager.addEventListener(CVEvent.SHELL, getData);
			//add an event listener to the timer, so that the display can be refreshed 
			starTimer.addEventListener(TimerEvent.TIMER, timerHandler);
			//screensaver coordinates 
			screenSaver.x=200;
			screenSaver.y=200;
			//add screensaver 
			addChild(screenSaver);
		}
		
		/**
		* Gets data about a CVEvent and creates constellations based on that data.
		*/
		public function getData (e : CVEvent) : void {
			//trace that data is being received 
			trace( "getting data " );
			//get the number of "blobs" of motion 
			var numBlobs : int = e.getNumBlobs();
			
			//if there is motion, the screensaver appears 
			if(numBlobs > 0)
			{
			removeChild(screensaver);
			}
			//the timer starts 
			starTimer.start();
		}
		
		//after 15 seconds, the screensaver reappears 
		 public function timerHandler(event:TimerEvent):void {
           
			   addChild(screenSaver);
		
		 }
	
}
}
