package{
	import flash.display.MovieClip;
	
		import flash.events.*;
	
	public class Strawberry extends Fruit{
	
		public function Strawberry(){
			fruitNumber = 4;
			 sound = new strawberrySound();
			
			 x=1000;
			 y=100;
			 
			stop();
			//addEventListener(MouseEvent.MOUSE_OVER, goStop);
			//addEventListener(MouseEvent.MOUSE_OUT, getOut);	 
			super();
		 
		}
	}
}