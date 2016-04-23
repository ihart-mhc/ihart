package {
	//import Box2D library
	//Box2D is an open source C++ engine for simulating rigid bodies in 2D.
	//http://box2d.org/about/
	import Box2D.Collision.*;
	import Box2D.Collision.Shapes.*;
	import Box2D.Dynamics.Contacts.*;
	import Box2D.Dynamics.*;
	import Box2D.Common.Math.*;
	import Box2D.Common.*;
	import flash.display.*;
	
	//import library from folders
	import com.jtuttle.box2d.b2Actor;
	import Box2D.Dynamics.b2Body;
	/*	import com.jtuttle.box2d.b2Actor;	import Box2D.Collision.Shapes.b2Shape;	import Box2D.Collision.b2ContactPoint;	import Box2D.Collision.b2WorldManifold;	import Box2D.Common.Math.b2Vec2;	import Box2D.Dynamics.Contacts.b2Contact;	import Box2D.Dynamics.b2Body;	import Box2D.Dynamics.b2ContactListener;	import Box2D.Dynamics.b2Fixture;*/	import flash.display.MovieClip;	public class Basket extends b2Actor {		public function Basket(body:b2Body){			super(body,new basketMove());		}	}				}