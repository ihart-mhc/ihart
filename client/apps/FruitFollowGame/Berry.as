﻿package{	import flash.display.MovieClip;			import flash.events.*;		public class Berry extends Fruit{			public function Berry(){			fruitNumber = 2;			sound = new berrySound();			x=530;			y=100;//			x=700;//			y=400;		 			stop();			//addEventListener(MouseEvent.MOUSE_OVER, goStop);			// addEventListener(MouseEvent.MOUSE_OUT, getOut);	 			super();		}	}}