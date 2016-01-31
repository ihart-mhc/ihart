//Author: (Collaborated) Barsha Shrestha//import flash.display.Shape;//import flash.geom.Matrix;//import flash.display.BitmapData;/*class : GameBoard*/ package {    import flash.display.MovieClip;	import flash.events.*;	import flash.utils.*;	import flash.events.Event;	import flash.display.DisplayObject;	import ihart.event.*;	import flash.geom.Point;	import flash.geom.Rectangle;
	 import flash.geom.ColorTransform;	//import flashx.textLayout.operations.InsertTextOperation;		import flash.utils.Timer;		     /**     * GameBoard is a class linked to a MovieClip Symbol.     * Select areas of interest in order: Apple, Banana, Blueberry, Lime, Start      */    public class GameBoard extends MovieClip    {		// allow CVEvent (motion) or mouse events (clicking)		public static var VISION : Boolean = true;		public static var MOUSE : Boolean = true;				public static var INSTRUCTIONS_VIEW_TIME : int = 50;		public static var WAIT_TIME : int = 300;		public static var PAUSE_TIME : int = 20;		public static var CV_DELAY : int = 500;			private var hostName:String = "localhost"; //host name for socket	private var port:uint = 5204; //port number	private var m : MovieClip; //movie clip to move around		//create a cvManager to dispatch a whole blob event	private var cvManager1_apple : CVManager;	private var cvManager1_banana : CVManager;	private var cvManager1_blueberry : CVManager;	private var cvManager1_lime : CVManager;
	private var currentblob: BlobPaint;	
	private var blobvector : Vector.<BlobPaint> = new Vector.<BlobPaint>();
	private var timer : Timer;	
			//private var cvManager1_strawberry : CVManager;	// var cvManager1_orange : CVManager;	private var cvManager_start : CVManager;			var seq_length : int = 2;		        /********************** INSTANCE PROPERTIES *********************/        // Store the arrays of the users input and the correct fruit sequence		var fruitArray : Array;		//var userSequence : Array;		var person : DisplayObject;				var seqy : Sequence;				var ansArray:Array;				var currentSeqSpot : int;				var tick : int;		var pauseTick : int;		var pauseTimer : Timer;		var cvTimer : Timer;				var userArray : Array;				var currentUserSpot :int;				//previous person location (last ihart event)		var previousPersonX:int=0;		var previousPersonY:int=0;				// if user is allowed to play, this is true		var userCanPlay,expectingUserInput, pausingForUserPlay, pauseBeforeUserCanPlay, cvEventsAllowed : Boolean;			// horrible setup, but ASJ is hacking... 4/18/14		var screenIsVisible : Boolean;				var numWins, numLosses : int;
		         /************************ INSTANCE METHODS **********************/        /**         * Constructor for the GameBoard class         */        public function GameBoard()         {			// horrible setup, but ASJ is hacking... 4/18/14			this.instructionsScreen = instructionsScreen;			instructionsScreen.visible = false;						userCanPlay = false;						tick = -1;			currentSeqSpot = 0;			currentUserSpot = 0;			seqy = new Sequence(seq_length);						//put all instances of fruit symbols in a array			fruitArray = new Array(4);						fruitArray[0] = new Apple();			fruitArray[1] = new Banana();			fruitArray[2] = new Berry();			fruitArray[3] = new Green();						/*fruitArray[0].x = 100;			fruitArray[0].y= 100;						fruitArray[1].x = 1000;			fruitArray[1].y = 100;						fruitArray[2].x = 100;			fruitArray[2].y = 600;						fruitArray[3].x = 1000;			fruitArray[3].y = 600;*/						//fruitArray[4] = new Strawberry();			//fruitArray[5] = new Orange();						for(var i : int; i < fruitArray.length; i++){				addChild(fruitArray[i]);								fruitArray[i].addEventListener("SequenceAnimationOver", playNextSequenceItem);						}									if ( VISION )			{				cvManager1_apple = new CVManager(hostName, port);				cvManager1_banana = new CVManager(hostName, port);				cvManager1_blueberry = new CVManager(hostName, port,2);				cvManager1_lime = new CVManager(hostName, port,3);				//cvManager1_strawberry = new CVManager(hostName, port,4);				//cvManager1_orange = new CVManager(hostName, port,5);								//we must add an event listener to the cv manager in order to know when				//we have received data										cvManager1_banana.addEventListener(CVEvent.SHELL, getData);				/*cvManager1_banana.addEventListener(CVEvent.SHELL, getData_banana);				cvManager1_blueberry.addEventListener(CVEvent.SHELL, getData_blueberry);				cvManager1_lime.addEventListener(CVEvent.SHELL, getData_lime);*/				//cvManager1_strawberry.addEventListener(CVEvent.SHELL, getData_strawberry);				//cvManager1_orange.addEventListener(CVEvent.SHELL, getData_orange);												cvManager_start = new CVManager(hostName, port);				// cvManager_start.addEventListener(CVEvent.SHELL);									cvEventsAllowed = true;			}						if ( MOUSE )			{				fruitArray[0].addEventListener( MouseEvent.CLICK, getData_apple);				fruitArray[1].addEventListener( MouseEvent.CLICK, getData_banana);				fruitArray[2].addEventListener( MouseEvent.CLICK, getData_blueberry);				fruitArray[3].addEventListener( MouseEvent.CLICK, getData_lime);				//fruitArray[4].addEventListener( MouseEvent.CLICK, getData_strawberry);				//fruitArray[5].addEventListener( MouseEvent.CLICK, getData_orange);			}						numWins = 0;			numLosses = 0;			updateTally();						//sequence length is not fixed anymore			userArray = new Array(seq_length);			//let all arrays have no fruits (0,1,2,3,4,5) for now			var ua:int; 			for (ua = 0; ua < seq_length; ua++) 			{				userArray[ua] = -1;			}									addEventListener( "SequenceAllOver", startUserPlay );										//everything is false in the beginning before the game starts			expectingUserInput = false;			pausingForUserPlay = false;			pauseBeforeUserCanPlay = false;						screenIsVisible = false;						//game has started			enableStartBtn();						cvTimer = new Timer( CV_DELAY );			cvTimer.addEventListener(TimerEvent.TIMER, allowCVEvents );		}				private function allowCVEvents( e : Event ) : void		{			cvEventsAllowed = true;			cvTimer.stop();		}					//resize function for main game stage...need to check this out				public function resizeContents(e : Event ) : void		{			trace( "resize!" );			 bg.width= stage.width;			 bg.height= stage.height;		}						//to update the score for the user and display it		private function updateTally() : void{			winsDisplay.text = numWins.toString();					}				public function enableStartBtn() : void		{			startBtn.visible = true;						if ( VISION )				cvManager_start.addEventListener( CVEvent.SHELL, startGame );			if ( MOUSE )				startBtn.addEventListener( MouseEvent.CLICK, startGame );		}				public function startGame( e : Event ) : void		{			if ( VISION )				cvManager_start.removeEventListener( CVEvent.SHELL, startGame );			startBtn.visible = false;			// show instructions			instructionsScreen.gotoAndStop( "instructions" );			showScreen( instructionsScreen );					}		public function startUserPlay( e : Event ):void		{			trace( "sequence is over -- user can almost play!" );						// wait a couple seconds before allowing selection			pauseTick = 0;			addEventListener( Event.ENTER_FRAME, pauseTickFunction );			pausingForUserPlay = true;					}				public function allowUserToPlay() : void{						// now user can play			userCanPlay = true;			trace( "user can play!" );						// time out if no one tries to play			tick = 0;			addEventListener( Event.ENTER_FRAME, tickFunction );			expectingUserInput = true;		}		public function resetGame(): void{			// user should not be allowed to play			userCanPlay = false;			trace( "RESETTING - user can't play!" );						for(var i =0; i < fruitArray.length; i++){				fruitArray[i].getOut();			}						currentSeqSpot = 0;			currentUserSpot = 0;						//set everything back to -1, like in the beginning			userArray = new Array(seq_length);			var ua:int; 			for (ua = 0; ua < seq_length; ua++) 			{				userArray[ua] = -1;			}									playEntireSequence();		}				private function showScreen( s : MovieClip ) : void		{			//trace( "show screen" );			userCanPlay = false;			s.visible = true;						screenIsVisible = true;			tick = 0;			addEventListener( Event.ENTER_FRAME, tickFunction );		}				public function loseGame(): void{			for(var i =0; i < fruitArray.length; i++){				fruitArray[i].killFruit();			}						// show lose			instructionsScreen.gotoAndStop( "lose" );			showScreen( instructionsScreen );												numWins=0;			numLosses=0;			updateTally();			//reset seq_length to 2			seq_length=2;			//new instance to restart from sequence of 2 in the beginning			seqy = new Sequence(seq_length);		}				public function winGame(): void{						// show win			instructionsScreen.gotoAndStop( "win" );			showScreen( instructionsScreen );						numWins++;			updateTally();				seq_length++;			//new instance to restart from sequence of 2 in the beginning			seqy = new Sequence(seq_length);			//update sequence_length			//updateSequenceLength();					}						public function playEntireSequence () : void{			ansArray = seqy.createSequence();			currentSeqSpot = -1;						playNextSequenceItem(null);					}				private function playNextSequenceItem(t:Event):void{						if(currentSeqSpot < ansArray.length - 1){				currentSeqSpot++;				fruitArray[ansArray[currentSeqSpot]].playSequenceAnimation();			}			else{								pauseTimer = new Timer( PAUSE_TIME );								pauseTimer.addEventListener(TimerEvent.TIMER, allowUserToStart);				pauseTimer.start();//				pauseTick = 0;		//		pauseBeforeUserCanPlay = true;				//addEventListener( Event.ENTER_FRAME, pauseTickFunction );			}		}				/*		public function setHitObject (persony : DisplayObject){			person = persony;			previousPersonX = person.x;			previousPersonY = person.y;		}		*/		// this function is attached to the animation tick		// and is invoked "constantly"		// we check for collisions		public function tickFunction(e: Event) : void {				tick++;			trace( "tick: " + tick );			if ( screenIsVisible && (tick > INSTRUCTIONS_VIEW_TIME) )			{				// make them invisible				instructionsScreen.visible = false;								screenIsVisible = false;				removeEventListener( Event.ENTER_FRAME, tickFunction );				resetGame();			}			if ( expectingUserInput && tick > WAIT_TIME )			{				// assume the user has left and show the waiting screen				trace( "user must have left" );				enableStartBtn();				expectingUserInput = false;				removeEventListener( Event.ENTER_FRAME, tickFunction );			}					}				public function pauseTickFunction(e: Event) : void {				pauseTick++;			trace( "pauseTick: " + pauseTick );			if ( pausingForUserPlay && pauseTick > PAUSE_TIME )			{				allowUserToPlay();								pausingForUserPlay = false;				removeEventListener( Event.ENTER_FRAME, pauseTickFunction );			}/*			if ( pauseBeforeUserCanPlay && pauseTick > PAUSE_TIME )			{								dispatchEvent(new Event("SequenceAllOver"));								pauseBeforeUserCanPlay = false;				removeEventListener( Event.ENTER_FRAME, pauseTickFunction );			}*/		}				private function allowUserToStart( e : Event )		{			dispatchEvent(new Event("SequenceAllOver"));			pauseTimer.stop();		}		/*		public function checkCollisions() : void{			trace( "collision check" );			for(var i : int; i < fruitArray.length; i++){				// if the person is hitting this fruit				if ( person.hitTestObject( fruitArray[i] ) && !fruitArray[i].isLitUp()) {					if((tick >= 2) || (tick == -1)){						fruitArray[i].playSound();						fruitArray[i].goStop();//						tick = 0;						generateUserSeq(i);					}else{						//tick++;					}					return;				}				// the person is not hitting this fruit				else				{					if ( fruitArray[i].isLitUp() )					{						// if the fruit was lit up						// make it stop						fruitArray[i].getOut();						//tick = -1;					}				}			}		}*/				//method to check if user generated sequence is the computer generated one		//display win or loss accordingly		public function generateUserSeq(i: int) : void{			if(currentUserSpot < seq_length){				if(userArray[currentUserSpot] == -1){					userArray[currentUserSpot] = i;					currentUserSpot ++;					trace("not done yet, but userArray is: " + userArray);				}				if(currentUserSpot == seq_length){					userCanPlay = false;										var result: Boolean = seqy.checkSequence(userArray);					trace("done and userArray is: " + userArray);					trace("result is: " + result);					if(result){						winGame();					}else{						loseGame();					}				}			}		}		/*		public function checkCollisionsRect(rect:Rectangle) : void{			for(var i : int; i < fruitArray.length; i++){				// if the person is hitting this fruit				if ( person.hitTestObject( fruitArray[i] ) && !fruitArray[i].isLitUp()) {					if((tick >= 5) || (tick == -1)){						fruitArray[i].playSound();						fruitArray[i].goStop();						tick = 0;						generateUserSeq(i);					}else{						//tick++;					}					return;				}				// the person is not hitting this fruit				else				{					if ( fruitArray[i].isLitUp() )					{						// if the fruit was lit up						// make it stop						fruitArray[i].getOut();						//tick = -1;					}				}			}		}						*/		//generate automated sequence that computer shows first		private function playFruitAnimation(index:int):void{			// if user isn't allowed to play yet			if ( !userCanPlay || !cvEventsAllowed )				return;			else			{				userCanPlay = false;			//if((tick >= 3) || (tick == -1)){				fruitArray[index].playSequenceAnimation();				generateUserSeq(index);								cvEventsAllowed = false;				cvTimer.start();			}				//tick=0;			//}					}							private function getData_banana(e : Event) : void{
			
						playFruitAnimation(1);			trace("BANANA!");					}				private function getData_blueberry(e : Event) : void{			playFruitAnimation(2);			trace("BLUEBERRY!");					}				private function getData_lime(e : Event) : void{			playFruitAnimation(3);			trace("LIME!");					}	
		
		private function getData_apple(e : Event) : void{
		
			//skinnyPoint(e);
			playFruitAnimation(0);
			
			trace(" THERE IS APPLE!");
		}	
		
		private function getData( e: CVEvent){
			var numBlobs : int = e.getNumBlobs();
			var blobX : Number;
			var blobY : Number;
			
			var blobForX: Number;
			var blobForY: Number;
			var colorTransform: ColorTransform;
			
				
			
			
			//trace("NEW SERIES OF BLOOOOOOBSSS");
			//save the blob's x and y values
			blobX = e.getX(0);
			blobY = e.getY(0);
			
			//for every blob there is on the screen
			for (var i : int = 0; i < numBlobs; i++) {
				
			currentblob = new BlobPaint();
			//trace (" ADD BLOBS PLEZ");
			currentblob = new BlobPaint();
			blobForX = e.getX(0);
			blobForY = e.getY(0);
				
			trace("blobX "+blobX);
			trace("blobY "+blobY);	
			
			currentblob.x = blobX;
			currentblob.y = blobY;
				
			removeOld();	
			addChild(currentblob);
			blobvector.push(currentblob);	
				
			
			
			
				
			//removeOld();
			trace(" ADD CHILDZZZZ");
				
			}
				
			
			
			if(blobX>=0 && blobX<=400 && blobY>=0 && blobY<=300)
			{
				playFruitAnimation(0);
			}
			
			else if(blobX>=600 && blobX<=1300 && blobY>=0 && blobY<=300)
			{
				playFruitAnimation(1);
			}
			
			else if(blobX>=0 && blobX <=400 && blobY>=400 && blobY<=700)
			{
				playFruitAnimation(2);
			}
			
			else if(blobX>=600 && blobX<=1300 && blobY>=400 && blobY<=700)
			{
				playFruitAnimation(3);
			}
			
		}		
			/*private function getData_strawberry(e : Event) : void{			playFruitAnimation(4);			trace("STRAWBERRY!");					}				private function getData_orange(e : Event) : void{			playFruitAnimation(5);			trace("ORANGE");					}*/				private function movePerson(bestX:int, bestY:int):void{						person.x = bestX;			person.y = bestY;		}				 private function completeHandler(e:TimerEvent):void {
            trace("TIME'S UP HALLELUJAH!!!");  
			
			removeChild(currentblob);
			 timer.stop();
        }
		public function removeOld () : void {
			
			//for every firework in the vector
			for (var i : int = 0; i < blobvector.length; i++) {
				
				//if the reference portion of the firework is not visible
				if (blobvector.length>=1) {
					
					//remove the firework from the screen
					removeChild(blobvector[i]);
					
					//remove the firework from the vector
					blobvector.splice(i, 1);

				}
				
			}
		}			}}