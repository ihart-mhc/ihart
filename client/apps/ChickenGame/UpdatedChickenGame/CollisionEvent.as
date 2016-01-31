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
	import Box2D.Dynamics.b2Body;
		import flash.events.Event;	/*import com.jtuttle.box2d.b2Actor;*/		public class CollisionEvent extends Event {		public static const COLLISION:String="COLLISION";		private var _actorA:b2Actor;		private var _actorB:b2Actor;				public function CollisionEvent(type:String, actorA:b2Actor,actorB:b2Actor) {			// constructor code			super(type);			_actorA=actorA;			_actorB=actorB;		}				public function get actorA():b2Actor{return _actorA;}		public function get actorB():b2Actor{return _actorB;}	}	}