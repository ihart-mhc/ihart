/**
HelloWorld.as
@author Pavlina Lejskova '15
iHart Independent Study Spring '15

This is a simple iHart application for programmers who want to learn iHart application development.
The application displays a "Hello World" sign and plays a "Hello World" sound in reaction to movement.
**/
package  {
	
	import ihart.event.*; // IMPORT THE IHART LIBRARY
	
	import flash.display.MovieClip;
	
	import flash.media.Sound;
	
	import flash.utils.Timer;
	import flash.events.TimerEvent;
	
	public class HelloWorld extends MovieClip{
		
		/******************** IHART SETUP ********************/
		
		// Set up the socket with localhost, using port 5204
		private var hostName:String = "localhost";
        private var port:uint = 5204;
		
		// Set up a cvManager to handle CVEvents
		private var cvManager:CVManager;
		
		/*****************************************************/
		
		// A vector to hold the "Hello World" signs
		private var signs:Vector.<Sign> = new Vector.<Sign>();;

		// A variable to hold the "Hello World" sound
		private var sound:Sound = new HWSound();;

		// A timer for the data handler, so we don't have a million sounds and signs at once
		var delay : int = 15;
		var repeat : int = 0;
		var timer : Timer = new Timer(delay, repeat);
		
				
		// A counter for the timer so we know when to stop
		var INPUT_DELAY : int = 250;
		var counter : int = 0;

		/**
		* In the constructor initialize the cvManager and add an event listener to it.
		*/
		public function HelloWorld() {
			cvManager = new CVManager(hostName, port);
			cvManager.addEventListener(CVEvent.SHELL, getData);
			
			// Start the timer
			timer.addEventListener(TimerEvent.TIMER, delayInput);
		}
		
		/**
		* In the getData function the CVEvent data is received
		* and can be use to create an interactive response.
		*/
		public function getData(e:CVEvent):void {
			
			// A Blob represents movement
			var numBlobs:int = e.getNumBlobs();
			
			var currentSign:Sign;
			
			// For every blob
			for (var i:int = 0; i < numBlobs; i++) {
				
				// Create a new "Hello World" sign
				currentSign = new Sign();
				
				// Assign it location based on the blob coordinates
				currentSign.x = e.getX(i);
				currentSign.y = e.getY(i);
				
				// Add it to the screen
				addChild(currentSign);
				
				// Push the sign to the signs vector
				signs.push(currentSign);
			}
			
			// Play the "Hello World" sound
			if(counter == 0){
				sound.play();
				timer.start();
			}
		}
		
		/**
		* Delay the input
		**/
		function delayInput(e: TimerEvent){
	
			if(counter == INPUT_DELAY){
				counter = 0;
				timer.stop();
				return;
			}
	
			counter++;
		}
	}
}