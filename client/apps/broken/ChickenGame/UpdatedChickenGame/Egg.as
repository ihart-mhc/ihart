package  {
	//import Box2D library
	//Box2D is an open source C++ engine for simulating rigid bodies in 2D.
	//http://box2d.org/about/
	import Box2D.Collision.*;
	import Box2D.Collision.Shapes.*;
	import Box2D.Dynamics.Contacts.*;
	import Box2D.Dynamics.*;
	import Box2D.Common.Math.*;
	import Box2D.Common.*;
		//import library from folders
	import com.jtuttle.box2d.b2Actor;
	import Box2D.Dynamics.b2Body;	import flash.display.MovieClip;	public class Egg extends b2Actor{		public function Egg(body:b2Body) {			// constructor code			super(body,new EggDrop());			//_costume.width=_body.get		}	}	}