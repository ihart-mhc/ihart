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
	/*	import Box2D.Collision.Shapes.b2Shape;	import Box2D.Collision.b2ContactPoint;	import Box2D.Collision.b2WorldManifold;	import Box2D.Common.Math.b2Vec2;	import Box2D.Dynamics.Contacts.b2Contact;	import Box2D.Dynamics.b2Body;	import Box2D.Dynamics.b2ContactListener;	import Box2D.Dynamics.b2Fixture;		import com.jtuttle.box2d.b2Actor;*/
			import flash.events.Event;	import flash.events.EventDispatcher;	import flash.events.IEventDispatcher;		public class ContactListener extends b2ContactListener implements IEventDispatcher {		private var _eventDispatcher:EventDispatcher;				public function ContactListener() {			super();			_eventDispatcher = new EventDispatcher(this);		}				override public function BeginContact(contact:b2Contact):void {			super.BeginContact(contact);			//what are actorA and actorB?			var actorA:b2Actor = contact.GetFixtureA().GetBody().GetUserData();			var actorB:b2Actor = contact.GetFixtureB().GetBody().GetUserData();			dispatchEvent(new CollisionEvent(CollisionEvent.COLLISION,actorA,actorB));			//not sure what this is
/*			if(actorB is Egg){				if(actorA is Ground){				}							}			if(actorA is Egg){				if(actorB is Ground){				}			}			trace(actorA+"A" + "hit" +actorB+"B");*/		}						public function addEventListener(type:String, listener:Function, useCapture:Boolean = false, priority:int = 0, useWeakReference:Boolean = false):void {			_eventDispatcher.addEventListener(type, listener, useCapture, priority, useWeakReference);		}				public function dispatchEvent(event:Event):Boolean {			return _eventDispatcher.dispatchEvent(event);		}				public function hasEventListener(type:String):Boolean {			return _eventDispatcher.hasEventListener(type);		}				public function removeEventListener(type:String, listener:Function, useCapture:Boolean = false):void {			_eventDispatcher.removeEventListener(type, listener, useCapture);		}				public function willTrigger(type:String):Boolean {			return _eventDispatcher.willTrigger(type);		}	}}