package{
	import flash.display.MovieClip;
	
		import flash.events.*;
	
	public class Orange extends Fruit{
	
		public function Orange(){
			fruitNumber = 5;
			 sound = new bananaSound();
			
			 x=1230;
			 y=100;
			 
			stop();
			//addEventListener(MouseEvent.MOUSE_OVER, goStop);
			//addEventListener(MouseEvent.MOUSE_OUT, getOut);	 
			super();
		 
		}
	}
}