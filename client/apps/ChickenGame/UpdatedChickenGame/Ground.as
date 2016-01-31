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
	import Box2D.Dynamics.b2Body;	import flash.display.MovieClip;	public class Ground extends b2Actor{		public function Ground(body:b2Body){			super(body, new MovieClip());		}	}	}