﻿/**Jorge.as@author The iHart TeamCS395&295 iHart Independent Study Fall '14**/package  {		import flash.events.*;	import flash.display.MovieClip;	import ihart.event.*;	import flash.utils.Timer;    import flash.events.TimerEvent;	import flash.media.Sound;	import flash.net.URLRequest;		public class Jorge extends MovieClip{				//set up the socket with localhost, using port 5204		private var hostName:String = "localhost";		//private var hostName:String = "192.168.10.1"; //hallway        private var port:uint = 5204;		//set up a cvManager to handle our CVEvents		private var cvManager:CVManager;		//number of blobs		private var numBlobs: int;				//screensaver to be displayed when no movement is detected		private var screensaver:ScreenSaver;				//timers		private var feedingTimer:Timer;		private var runningJorgeTimer:Timer;				//screaming jorges		private var swimmingJorge:SwimmingJorge;		private var runningJorge:RunningJorge;				//hand		private var hand:Hand;				// Jorge screaming sound for running Jorge		private var sound:GooseSound = new GooseSound();				/**		 * Constructor initializes the cvManager and adds an event listener to it.		 */		public function Jorge() {			// Initialize the cvManager			cvManager = new CVManager(hostName, port);			cvManager.addEventListener(CVEvent.SHELL, getData);			numBlobs = 0;						// Initialize the hand			hand = new Hand();						// Initialize the timers			feedingTimer = new Timer(10000,1);			feedingTimer.addEventListener(TimerEvent.TIMER, feedingTimerHandler);			runningJorgeTimer = new Timer(7000,1);			runningJorgeTimer.addEventListener(TimerEvent.TIMER, runningJorgeTimerHandler);						// Initialize the screensaver			screensaver = new ScreenSaver();			addChild(screensaver);						// Initialize the jorges			swimmingJorge = new SwimmingJorge();			runningJorge = new RunningJorge();		}				/**		 *Gets data about a CVEvent and reacts appropriatelly.		 */		public function getData (e : CVEvent) : void {			trace( "Acquiring data... " );			numBlobs  = e.getNumBlobs();			var blobX : Number;			var blobY : Number;						//Initialize hand			for (var i : int = 0; i < numBlobs; i++) {				blobX = e.getX(i);				blobY = e.getY(i);				moveHand(blobX, blobY);			}						//if there is motion, the screensaver disappears 			if(numBlobs > 0)			{				removeChild(screensaver);				addChild(swimmingJorge);								// Start the timer				feedingTimer.start();			}		}				/**		 * Move hand.		 */		private function moveHand(x:int, y:int):void{			addChild(hand);			hand.x = x;			hand.y = 10;		}		 		 /**		 * After 10 seconds, the Jorge comes running.		 */		 public function feedingTimerHandler(event:TimerEvent):void {			   removeChild(swimmingJorge);			   addChild(runningJorge);			   runningJorgeTimer.start();			   // play screaming sound			   sound.play();			   cvManager.removeEventListener(CVEvent.SHELL, getData);		 }		 		  /**		 * After 7 seconds, the Jorge comes running.		 */		 public function  runningJorgeTimerHandler(event:TimerEvent):void {			   addChild(screensaver);			   removeChild(runningJorge);			   cvManager.addEventListener(CVEvent.SHELL, getData);		 }}}