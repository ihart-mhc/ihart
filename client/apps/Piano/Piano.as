﻿// Piano.as
// Attached to Piano.fla
package
{
	import flash.display.Sprite;
	import flash.media.Sound;
	import flash.media.SoundChannel;
	import flash.net.URLRequest;
	import flash.events.TimerEvent; 
    import flash.utils.Timer;
	import ihart.event.*;
	
	/**		
 	* Piano
	* @author Michelle DeVeaux
	* Listens for hull events and plays piano notes
	* based on the location of the hull.
	**/
	public class Piano extends Sprite 
	{
		// fields for setting up the socket with localhost, using port 5204
		private var hostName:String = "localhost";
		//private var hostName:String = "192.168.10.1"; //hallway
        private var port:uint = 5204;
		// create variable for each note and link it to the audio file
		// create a SoundChannel for each note
		// create a boolean for each note that tells whether or not the note is currently being played
		// create a timer for each note which will be set to correspond to the length of the audio clip
		private var pianoC:Sound = new Sound(new URLRequest("SoundClips/piano_middle_C.mp3"));
		private var soundChannelC : SoundChannel;
		private var playingC : Boolean = false;
		private var timerC : Timer;
		private var pianoCSharp:Sound = new Sound(new URLRequest("SoundClips/piano_C_sharp.mp3"));
		private var soundChannelCSharp : SoundChannel;
		private var playingCSharp : Boolean = false;
		private var timerCSharp : Timer;
		private var pianoD:Sound = new Sound(new URLRequest("SoundClips/piano_D.mp3"));
		private var soundChannelD : SoundChannel;
		private var playingD : Boolean = false;
		private var timerD : Timer;
		private var pianoDSharp:Sound = new Sound(new URLRequest("SoundClips/piano_D_sharp.mp3"));
		private var soundChannelDSharp : SoundChannel;
		private var playingDSharp : Boolean = false;
		private var timerDSharp : Timer;
		private var pianoE:Sound = new Sound (new URLRequest("SoundClips/piano_E.mp3"));
		private var soundChannelE : SoundChannel;
		private var playingE : Boolean = false;
		private var timerE : Timer;
		private var pianoF:Sound = new Sound (new URLRequest("SoundClips/piano_F.mp3"));
		private var soundChannelF : SoundChannel;
		private var playingF : Boolean = false;
		private var timerF : Timer;
		private var pianoFSharp:Sound = new Sound (new URLRequest("SoundClips/piano_F_sharp.mp3"));
		private var soundChannelFSharp : SoundChannel;
		private var playingFSharp : Boolean = false;
		private var timerFSharp : Timer;
		private var pianoG:Sound = new Sound (new URLRequest("SoundClips/piano_G.mp3"));
		private var soundChannelG : SoundChannel;
		private var playingG : Boolean = false;
		private var timerG : Timer;
		private var pianoGSharp:Sound = new Sound (new URLRequest("SoundClips/piano_G_sharp.mp3"));
		private var soundChannelGSharp : SoundChannel;
		private var playingGSharp : Boolean = false;
		private var timerGSharp : Timer;
		private var pianoA:Sound = new Sound (new URLRequest("SoundClips/piano_A.mp3"));
		private var soundChannelA : SoundChannel;
		private var playingA : Boolean = false;
		private var timerA : Timer;
		private var pianoASharp:Sound = new Sound(new URLRequest("SoundClips/piano_A_sharp.mp3")); 
		private var soundChannelASharp : SoundChannel;
		private var playingASharp : Boolean = false;
		private var timerASharp : Timer;
		private var pianoB:Sound = new Sound(new URLRequest("SoundClips/piano_B.mp3"));
		private var soundChannelB : SoundChannel;
		private var playingB : Boolean = false;
		private var timerB : Timer;
		private var coordinateWidth:int = 500;
		private var coordinateLength:int = 800;
		// the keyLength is the length of each white key on the bottom half of the projection
		// it is equal to the coordinateLength divided by the number of white keys
		private var keyLength : int = coordinateLength/7;
		//delay tells how long the timer should run for
		// in this case, 5 seconds
		private var delay : int = 3500;
		// repeat tells how many times the timer will repeat
		// in this case, we only want the timer to run once
		private var repeat : int = 1;
		
	
		/**
		 * Constructor
		 **/
		public function Piano()
		{
			trace( "hello!" );
			
			// create a CVManager to mange CV events
			var cvManager : CVManager = new CVManager( hostName, port );
			//register for HULL events, hook up to hullsArrive method
			cvManager.addEventListener( CVEvent.SHELL, hullsArrive );
			//create timers of the specified length and number of repeats 
			timerC = new Timer(delay, repeat);
			timerCSharp = new Timer(delay, repeat);
			timerD = new Timer(delay, repeat);
			timerDSharp = new Timer(delay, repeat);
			timerE = new Timer(delay, repeat);
			timerF = new Timer(delay, repeat);
			timerFSharp = new Timer(delay, repeat);
			timerG = new Timer(delay, repeat);
			timerGSharp = new Timer(delay, repeat);
			timerA = new Timer(delay, repeat);
			timerASharp = new Timer(delay, repeat);
			timerB = new Timer(delay, repeat);
			//add event listeners so that when a timer is complete, 
			//a function can be called to change the appropriate boolean back to false
			timerC.addEventListener(TimerEvent.TIMER_COMPLETE, timerCComplete);
			timerCSharp.addEventListener(TimerEvent.TIMER_COMPLETE, timerCSharpComplete);
			timerD.addEventListener(TimerEvent.TIMER_COMPLETE, timerDComplete);
			timerDSharp.addEventListener(TimerEvent.TIMER_COMPLETE, timerDSharpComplete);
			timerE.addEventListener(TimerEvent.TIMER_COMPLETE, timerEComplete);
			timerF.addEventListener(TimerEvent.TIMER_COMPLETE, timerFComplete);
			timerFSharp.addEventListener(TimerEvent.TIMER_COMPLETE, timerFSharpComplete);
			timerG.addEventListener(TimerEvent.TIMER_COMPLETE, timerGComplete);
			timerGSharp.addEventListener(TimerEvent.TIMER_COMPLETE, timerGSharpComplete);
			timerA.addEventListener(TimerEvent.TIMER_COMPLETE, timerAComplete);
			timerASharp.addEventListener(TimerEvent.TIMER_COMPLETE, timerASharpComplete);
			timerB.addEventListener(TimerEvent.TIMER_COMPLETE, timerBComplete);
		}
		
		/** 
		 * Called when hulls event occurs.
		 **/
		public function hullsArrive( e : CVEvent )
		{
			// store the number of received hulls
			// ask the event to give us the data
			var numHulls : int = e.getNumBlobs();
			trace( "got " + numHulls + " hulls!" );
			// declare variable for loop
			// for each hull
			for ( var i : int = 0; i < numHulls; i++ )
			{
				// if the hull is located in the lower half of the projection
				// this means that there are only evenly spaced white keys
				if (e.getY(i)>=(coordinateWidth/2)) {
					//divide the x coordinate of the hull by the keyLength to determine which key should be played
					//if the result is between 0 and 1, the first white key (C) should be played 
					if(((e.getX(i)/(keyLength))>=0)&&((e.getX(i)/(keyLength))<1)&&(playingC==false)) {
						trace("PLAY C");
						//play the audio clip found in soundChannelC
						soundChannelC = pianoC.play();
						//change the boolean playingC to true
						playingC = true;
						//start the timer for C
						timerC.start();
					}
					// if the result is between 1 and 2, the second white key (D) should be played
					if(((e.getX(i)/(keyLength))>=1)&&((e.getX(i)/(keyLength))<2)&&(playingD==false)) {
						trace("PLAY D");
						soundChannelD = pianoD.play();
						playingD = true;
						timerD.start();
					}
					// result between 2 and 3, play E
					if(((e.getX(i)/(keyLength))>=2)&&((e.getX(i)/(keyLength))<3)&&(playingE==false)) {
						trace("PLAY E");
						soundChannelE = pianoE.play();
						playingE = true;
						timerE.start();
					}
					// result between 3 and 4, play F
					if(((e.getX(i)/(keyLength))>=3)&&((e.getX(i)/(keyLength))<4)&&(playingF==false)) {
						trace("PLAY F");
						soundChannelF = pianoF.play();
						playingF = true;
						timerF.start();
					}
					// result between 4 and 5, play G
					if(((e.getX(i)/(keyLength))>=4)&&((e.getX(i)/(keyLength))<5)&&(playingG==false)) {
						trace("PLAY G");
						soundChannelG = pianoG.play();
						playingG = true;
						timerG.start();
					}
					// result between 5 and 6, play A
					if(((e.getX(i)/(keyLength))>=5)&&((e.getX(i)/(keyLength))<6)&&(playingA==false)) {
						trace("PLAY A");
						soundChannelA = pianoA.play();
						playingA = true;
						timerA.start();
					}
					// result between 6 and 7, play B
					if(((e.getX(i)/(keyLength))>=6)&&((e.getX(i)/(keyLength))<=7)&&(playingB==false)) {
						trace("PLAY B");
						soundChannelB = pianoB.play();
						playingB = true;
						timerB.start();
					}
				}
				// if the hull is located in the upper half of the projection
				// this means that there are white and black keys to deal with
				if (e.getY(i)<(coordinateWidth/2)) {
					// figure that the black keys take over 1/4 of the white key lengths surrounding it on both sides
					// so the first black key, C#, goes from 3/4 of the first white key (C) 
					// to 1/4 of the second white key (D) on the top half of the projection only
					// also, the boolean that tells whether each note is currently being played must be set to false
					if ((e.getX(i)>=0)&&(e.getX(i)<(.75*keyLength))&&(playingC==false)) {
						trace("PLAY C FROM TOP HALF");
						//play the audio clip found in soundChannelC
						soundChannelC = pianoC.play();
						//change the boolean playingC to true
						playingC = true;
						//start the timer for C
						timerC.start();
					}
					if ((e.getX(i)>=(.75*keyLength))&&(e.getX(i)<(1.25*keyLength))&&(playingCSharp==false)) {
						trace("PLAY C#");
						soundChannelCSharp = pianoCSharp.play();
						playingCSharp = true;
						timerCSharp.start();
					}
					if ((e.getX(i)>=(1.25*keyLength))&&(e.getX(i)<(1.75*keyLength))&&(playingD==false)) {
						trace("PLAY D FROM TOP HALF");
						soundChannelD = pianoD.play();
						playingD = true;
						timerD.start();
					}
					if ((e.getX(i)>=(1.75*keyLength))&&(e.getX(i)<(2.25*keyLength))&&(playingDSharp==false)) {
						trace("PLAY D#");
						soundChannelDSharp = pianoDSharp.play();
						playingDSharp = true;
						timerDSharp.start();
					}
					// E does not have a black key to the right of it, so on the top half,
					// the E key extends all the way to 3*keyLength
					if ((e.getX(i)>=(2.25*keyLength))&&(e.getX(i)<(3*keyLength))&&(playingE==false)) {
						trace("PLAY E FROM TOP HALF");
						soundChannelE = pianoE.play();
						playingE = true;
						timerE.start();
					}
					if ((e.getX(i)>=(3*keyLength))&&(e.getX(i)<(3.75*keyLength))&&(playingF==false)) {
						trace("PLAY F FROM TOP HALF");
						soundChannelF = pianoF.play();
						playingF = true;
						timerF.start();
					}
					if ((e.getX(i)>=(3.75*keyLength))&&(e.getX(i)<(4.25*keyLength))&&(playingFSharp==false)) {
						trace("PLAY F#");
						soundChannelFSharp = pianoFSharp.play();
						playingFSharp = true;
						timerFSharp.start();
					}
					if ((e.getX(i)>=(4.25*keyLength))&&(e.getX(i)<(4.75*keyLength))&&(playingG==false)) {
						trace("PLAY G FROM TOP HALF");
						soundChannelG = pianoG.play();
						playingG = true;
						timerG.start();
					}
					if ((e.getX(i)>=(4.75*keyLength))&&(e.getX(i)<(5.25*keyLength))&&(playingGSharp==false)) {
						trace("PLAY G#");
						soundChannelGSharp = pianoGSharp.play();
						playingGSharp = true;
						timerGSharp.start();
					}
					if ((e.getX(i)>=(5.25*keyLength))&&(e.getX(i)<(5.75*keyLength))&&(playingA==false)) {
						trace("PLAY A FROM TOP HALF");
						soundChannelA = pianoA.play();
						playingA = true;
						timerA.start();
					}
					if ((e.getX(i)>=(5.75*keyLength))&&(e.getX(i)<(6.25*keyLength))&&(playingASharp==false)) {
						trace("PLAY A#");
						soundChannelASharp = pianoASharp.play();
						playingASharp = true;
						timerASharp.start();
					}
					// B also does not have a black key to the right of it, so on the top half,
					// the B key extends all the way to 7*keyLength
					if ((e.getX(i)>=(6.25*keyLength))&&(e.getX(i)<=(7*keyLength))&&(playingB==false)) {
						trace("PLAY B FROM TOP HALF");
						soundChannelB = pianoB.play();
						playingB = true;
						timerB.start();
					}
				}
			}
		}
		//the timerComplete functions are called when the timers are completed
		//when these functions are called, their respective notes should have finished playing
		//they set the appropriate boolean back to false to tell us that the notes are no longer being played
		public function timerCComplete(e: TimerEvent) : void{
			trace("TIMER C COMPLETE");
			playingC = false;
		}
		public function timerCSharpComplete(e: TimerEvent) : void{
			trace("TIMER CSHARP COMPLETE");
			playingCSharp = false;
		}
		public function timerDComplete(e: TimerEvent) : void{
			trace("TIMER D COMPLETE");
			playingD = false;
		}
		public function timerDSharpComplete(e: TimerEvent) : void {
			trace("TIMER DSHARP COMPLETE");
			playingDSharp = false;
		}
		public function timerEComplete(e: TimerEvent) : void {
			trace("TIMER E COMPLETE");
			playingE = false;
		}
		public function timerFComplete(e: TimerEvent) : void {
			trace("TIMER F COMPLETE");
			playingF = false;
		}
		public function timerFSharpComplete(e: TimerEvent) : void {
			trace("TIMER FSHARP COMPLETE");
			playingFSharp = false;
		}
		public function timerGComplete(e: TimerEvent) : void {
			trace("TIMER G COMPLETE");
			playingG = false;
		}
		public function timerGSharpComplete(e: TimerEvent) : void {
			trace("TIMER GSHARP COMPLETE");
			playingGSharp = false;
		}
		public function timerAComplete(e: TimerEvent) : void {
			trace("TIMER A COMPLETE");
			playingA = false;
		}
		public function timerASharpComplete(e: TimerEvent) : void {
			trace("TIMER ASHARP COMPLETE");
			playingASharp = false;
		}
		public function timerBComplete(e: TimerEvent) : void {
			trace("TIMER B COMPLETE");
			playingB = false;
		}		
	}
}		   
																					 
																					 
																					
