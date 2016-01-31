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

	//import library from folders
	import com.jtuttle.box2d.b2Actor;
	import Box2D.Dynamics.b2Body;
	import com.jtuttle.box2d.b2Utils;
	import com.jtuttle.box2d.b2Values;
	/*	import Box2D.Collision.Shapes.b2CircleShape;	import Box2D.Collision.Shapes.b2PolygonShape;	import Box2D.Collision.b2AABB;	import Box2D.Common.Math.b2Vec2;	import Box2D.Dynamics.b2Body;	import Box2D.Dynamics.b2BodyDef;	import Box2D.Dynamics.b2DebugDraw;	import Box2D.Dynamics.b2FixtureDef;	import Box2D.Dynamics.b2World;	import Box2D.Dynamics.b2DestructionListener;	import com.jtuttle.box2d.b2Utils;	import com.jtuttle.box2d.b2Values;*/
	import flash.net.XMLSocket;
	import flash.geom.Vector3D;
	import ihart.event.*;
	import flash.display.*;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.utils.Timer;
	import flash.events.*; //import com.jtuttle.box2d.b2Actor;
	import flash.text.*;
	import flash.display.IBitmapDrawable;
	import flash.display.MovieClip;
	import ihart.gui.CVButton;
	//stuff for moving chicken
/*	import fl.transitions.Tween;
	import fl.transitions.easing.*;
	import fl.transitions.TweenEvent;*/
 
	[SWF(width = "500", height = "500")]
	
	public class ChickenGame extends Sprite {
		private var numButtonWidth: Number = 100;
		private var numButtonHeight: Number = 50;
		private var world: b2World;
		private var chicken: Chicken;
		private var MOVE_STEP: int = 1;
		private var GAME_TIME: int = 30;
		private var missed: int = 0;
		private var got: int = 0;
		private var basket: Basket;
		private var t: Timer;
		private var timer: Timer;
		private var end: EndScreen
		private var MAX_EGGS: int = 20;
		private var arrayOfEggs: Array = new Array();
		private var timerForEggs: Timer;
		private var cvButton: CVButton;
		/**		* Fields		**/ //set up the socket with localhost, using port 5204
		protected var hostName: String = "localhost";
		protected var port: uint = 5204; //create a cvManager to dispatch a whole blob event
		private var cvManager: CVManager;
		/**		* Fields		**/ //constants
		private const DELAY: int = 10; //instances
		private var delay: int = DELAY;
		public function ChickenGame() {
			createWorld();
			createPins();
			createGround();
			createBasket();
			addChicken();
			//move the basket with keyboard
			stage.addEventListener(KeyboardEvent.KEY_DOWN, move);
			addEventListener(Event.ENTER_FRAME, onEnterFrame);
			addTimer();
			init();
		}
		private function init(): void {
			cvManager = new CVManager(hostName, port);
			cvManager.addEventListener(CVEvent.SHELL, getData);
		}
		/**		* CVEvent Listener getData get's the x and y coordinates from the		* CVEvent		**/
		//set position of the basket in corelation of ihart input
		//this code is wrong btw
		private function getData(e: CVEvent): void {
			trace("x: " + e.getX(0) + ", y: " + e.getY(0));
			//set position of the basket
			if (e.getX(0) > -1 && e.getY(0) > -1) {
				if (e.getX(0) < 1000) {
					if ((e.getY(0)) < 200) {
						trace("y<200");
						basket.body.SetPosition(new b2Vec2((e.getX(0) / 1000) * 17, basket.body.GetPosition().y));
						var found: Boolean = false;
						var n: int = 1;
						while (!found && n < e.getNumBlobs()) {
							if (!e.getY(n) > 300) {
								n++;
							} else {
								found = true;
							}
						}
						trace(basket.body.GetPosition().x);
						basket.body.SetPosition(new b2Vec2((e.getX(n) / 1000) * 17, basket.body.GetPosition().y));
					} else if (e.getY(n) > 300) {
						basket.body.SetPosition(new b2Vec2((e.getX(0) / 1000) * 17, basket.body.GetPosition().y));
						while (!found) {
							if (!e.getY(n) < 200) {
								n++;
							} else {
								found = true;
							}
						}
						basket.body.SetPosition(new b2Vec2((e.getX(n) / 1000) * 17, basket.body.GetPosition().y));
					}
				}
			}
		}
		//add timer
		private function addTimer(): void {
			t = new Timer(1000, 0);
			t.start();
			timerForEggs = new Timer(1000, 0);
			timerForEggs.start();
		}
		//add obstacles to the game
		private function createPins(): void {
			var pins: Array = [241, 81, 222, 81, 213, 88, 208, 94, 202, 100, 198, 106, 195, 113, 187, 93, 182, 98, 178, 103, 175, 109, 173, 114, 172, 120, 171, 127, 149, 128, 149, 120, 147, 113, 145, 108, 142, 103, 137, 98, 132, 94, 127, 90, 121, 86, 242, 123, 238, 127, 234, 131, 230, 135, 226, 139, 214, 151, 132, 124, 114, 124, 96, 124, 123, 140, 105, 140, 87, 140, 114, 156, 96, 156, 78, 156, 123, 172, 105, 172, 87, 172, 69, 172, 114, 188, 96, 188, 78, 188, 60, 188, 105, 204, 87, 204, 69, 204, 96, 220, 78, 220, 135, 202, 130, 206, 126, 210, 122, 215, 118, 220, 115, 226, 113, 232, 111, 238, 20, 191, 24, 193, 28, 196, 32, 200, 36, 204, 39, 208, 42, 211, 44, 215, 47, 219, 50, 224, 52, 228, 54, 233, 56, 238, 151, 202, 157, 206, 162, 211, 166, 216, 169, 221, 172, 227, 174, 233, 175, 239, 196, 169, 232, 169, 250, 169, 169, 185, 187, 185, 205, 185, 223, 185, 241, 185, 178, 201, 196, 201, 232, 201, 250, 201, 187, 217, 241, 217, 250, 233, 143, 220, 134, 236, 152, 236, 143, 252, 55, 280, 73, 280, 91, 280, 109, 280, 127, 280, 46, 296, 64, 296, 82, 296, 100, 296, 118, 296, 136, 296, 55, 312, 73, 312, 91, 312, 109, 312, 127, 312, 64, 330, 82, 330, 100, 330, 118, 330, 136, 330, 164, 314, 164, 320, 164, 326, 164, 332, 164, 338, 164, 344, 164, 350, 163, 356, 161, 362, 158, 367, 154, 370, 149, 372, 186, 314, 208, 314, 186, 400, 208, 400, 176, 414, 218, 414, 186, 340, 186, 346, 186, 352, 186, 358, 185, 364, 183, 370, 180, 375, 176, 378, 171, 380, 208, 340, 208, 346, 208, 352, 208, 358, 209, 364, 211, 370, 214, 375, 218, 378, 223, 380, 223, 264, 241, 264, 232, 282, 250, 282, 241, 298, 232, 314, 250, 314, 241, 330, 232, 346, 250, 346, 241, 362, 250, 378, ]; // Create 'pin'
			for (var i: int = 0; i < pins.length; i += 2) {
				var p: Pin = new Pin(b2Utils.createBall(pins[i], pins[i + 1], 1, b2Body.b2_kinematicBody, world));
				var p2: Pin = new Pin(b2Utils.createBall(500 - pins[i], pins[i + 1], 1, b2Body.b2_kinematicBody, world));
				addChild(p.costume);
				addChild(p2.costume);
			}
		} //create world with gravity and contact handling
		private function createWorld(): void {
			var gravity: b2Vec2 = new b2Vec2(0, 20); //var ignoreSleeping:Boolean = true;
			world = new b2World(gravity, true);
			var contactListener: ContactListener = new ContactListener()
			contactListener.addEventListener(CollisionEvent.COLLISION, handleCollision); //			contactListener.addEventListener(CollisionEvent.BOULDER_BOULDER_COLLISION, handleBoulderBoulderCollision);
			world.SetContactListener(contactListener);
		}
		private function handleCollision(e: CollisionEvent): void {
			if (e.actorB is Egg) {
				if (e.actorA is Ground) {
					trace("B hit ground");
					e.actorB.removalFlag = true;
					missed++;
					numMissed.text = missed.toString(); //e.actorB.destroy(); //world.DestroyBody(e.actorB.body);
				} else if (e.actorA is Basket) {
					trace("B hit Basket");
					e.actorB.removalFlag = true;
					got++;
					numGot.text = got.toString();
				}
			}
			if (e.actorA is Egg) {
				if (e.actorB is Ground) {
					trace("A hit ground");
				} else if (e.actorB is Basket) {
					trace("A hit Basket");
					e.actorA.removalFlag = true;
				}
			}
		} //create the ground
		private function createGround(): void {
			var body: b2Body = b2Utils.createBox(750 / 2, 490, 750 / 2 + 500, 10, b2Body.b2_kinematicBody, world);
			body.GetFixtureList().SetRestitution(1);
			var ground: Ground = new Ground(body); //			body.GetFixtureList().SetFriction(0);
		}
		//create the basket
		private function createBasket(): void {
			var body: b2Body = b2Utils.createBox(500 / 2, 450, 30, 20, b2Body.b2_kinematicBody, world);
			body.GetFixtureList().SetRestitution(1);
			basket = new Basket(body);
			addChild(basket.costume);
		}
		//create egg
		//egg is not the ball tbh
		private function createBall(): void { //for( var i:int = 0; i < 50; i += 1 ){ //chicken.GetPosition().x;
			if (arrayOfEggs.length <= MAX_EGGS) {
				var egg: Egg = new Egg(b2Utils.createBall(chicken.body.GetPosition().x * b2Values.PX_RATIO, 50, 6, b2Body.b2_dynamicBody, world));
				addChild(egg.costume);
				arrayOfEggs.push(egg);
			} //} //trace(chicken.body.GetPosition().x);
		}
		//what the hell is this?
		public function enableDebugDraw(): void {
			var debugSprite: Sprite = new Sprite();
			debugSprite.mouseEnabled = false;
			debugSprite.mouseChildren = false;
			addChild(debugSprite);
			var debugDraw: b2DebugDraw = new b2DebugDraw();
			debugDraw.SetSprite(debugSprite);
			debugDraw.SetDrawScale(b2Values.PX_RATIO);
			debugDraw.SetFillAlpha(0.5);
			debugDraw.SetLineThickness(2.0);
			debugDraw.SetFlags(b2DebugDraw.e_shapeBit);
			world.SetDebugDraw(debugDraw);
		}
		private function onEnterFrame(e: Event): void {
			physicsUpdate();
			animateActors();
			removeStuckEggs();
			moveChic();
			dropEggs();
		}
		//create eggs to fall down
		private function dropEggs() {
			if (timerForEggs.currentCount == 2) {
				createBall();
				timerForEggs.reset();
				timerForEggs.start();
			}
		}
		
/*		private function moveChic(e: TweenEvent): void
		{
			chicken = new Tween(box, "x", Elastic.easeInOut, box.x, Math.random() * stage.stageWidth + stage.y, 2, true);
			chicken.addEventListener(TweenEvent.MOTION_FINISH, startTween);
		}*/
		private function moveChic():void {
			//if ( chicken.body.GetPosition().x <= stage.stageWidth )
				//{
					//trace(chicken.body.GetPosition().x);
					var chicMove: Number = 0.1;
					//generate random move
					var randomMove: int = Math.random()*10;
						
					//chicken.body.GetPosition().x -= chicMove;
					if (chicken.body.GetPosition().x >= 18)
					{
						//flip the object
						//chicken.body.scaleY= -1;
						//move the chicken to the left
						chicken.body.GetPosition().x -= chicMove;
					}
					else if (chicken.body.GetPosition().x < 0)
					{
						//trace(chicken.body.GetPosition().x);
						chicken.body.GetPosition().x += chicMove;
					}
					else
						chicken.body.GetPosition().x -= chicMove;
						trace(chicken.body.GetPosition().x);
			//			timerForChic.reset();
			//		}
			//		else
			//			//chicken.body._rotation = 180;
			//			for (var j:int = 0; j < 3; j++)
			//		{
			//			chicken.body.GetPosition().x -= chicMove;
			//			//timerForChic.reset();
			//		}
			//	}
			//else
			//	{
			//		chicken.body.GetPosition().x = x;
			//	}
		//}
		}

		//remove stuck eggs everywhere
		private function removeStuckEggs(): void {
			for (var i: int = 0; i < arrayOfEggs.length; i++) {
				var egg: Egg = arrayOfEggs[i];
				if ((egg.body.GetLinearVelocity().x == 0) && (egg.body.GetLinearVelocity().y == 0)) {
					egg.removalFlag = true;
				}
			}
		}
		//make actors move?
		private function animateActors(): void {
			var b2: b2Body = world.GetBodyList();
			while (b2 != null) {
				var actor: b2Actor = b2.GetUserData();
				if (actor != null) {
					actor.updateCostume();
				}
				b2 = b2.GetNext();
			}
		}
		//this stuff helps eggs fall down
		public function physicsUpdate(): void {
			//make eggs disappear when touch the basket
			destroyBodies();

			//this specific line helps drop the egg down
			world.Step(1 / 30, 10, 10); //world.ClearForces()
			world.DrawDebugData();
			if (t != null) {
				timerText.text = (GAME_TIME - t.currentCount).toString();
				checkGameStatus();
			}
		}
		public function checkGameStatus(): void {
			if (t != null && t.currentCount == GAME_TIME) {
				t.stop();
				t = null;
				endGame();
			}
		}
		public function endGame(): void {
			world.SetDestructionListener(new b2DestructionListener());
			removeEventListener(Event.ENTER_FRAME, onEnterFrame);
			stage.removeEventListener(KeyboardEvent.KEY_DOWN, move);
			removeStuckEggs();
			for (var i: int; i < arrayOfEggs.length; i++) {
				removeChild(arrayOfEggs[i].costume);
			}
			removeChild(chicken.costume);
			removeChild(basket.costume);
			world.Step(1 / 30, 10, 10);
			world.ClearForces();
			createFinishScreen();
		}
		private function createFinishScreen(): void {
			end = new EndScreen();
			end.width = 400;
			end.height = 400;
			end.x = 250;
			end.y = 250;
			addChild(end);
			var xPosition: int = end.caughtScore.x - 10
			var yPosition: int = end.caughtScore.y + 5 + end.caughtScore.height / 2;
			for (var i: int = 0; i < got; i++) {
				var egg: EggDrop = new EggDrop();
				xPosition += (15 + egg.width);
				if (xPosition > 250) {
					xPosition = end.caughtScore.x
					yPosition += egg.height + 5;
				}
				egg.x = xPosition
				egg.y = yPosition
				end.addChild(egg);
			}
			xPosition = end.brokenScore.x - 10
			yPosition = end.brokenScore.y + 5 + end.brokenScore.height / 2;
			//add egg broken to the scene
			for (var j: int = 0; j < missed; j++) {
				var eb: EggBroken = new EggBroken();
				eb.width *= 0.4
				eb.height *= 0.4
				xPosition += (30 + egg.width);
				if (xPosition > 220) {
					xPosition = end.brokenScore.x
					yPosition += eb.height + 5;
				}
				eb.x = xPosition
				eb.y = yPosition
				end.addChild(eb);
			} ////Instructions Text //			var caughtScore:TextField = new TextField(); //			 //			var caughtScore_format:TextFormat = new TextFormat("Arial", 24, 0x000000); //   			//caughtScore_format.align = TextFormatAlign.LEFT; //			 //			//caughtScore.defaultTextFormat = caughtScore_format //			 //			caughtScore.x = - 200 //			caughtScore.y = -200 //			caughtScore.autoSize = TextFieldAutoSize.LEFT; //			caughtScore.text = "Caught Egg: " //			end.addChild(caughtScore); //			
			/*cvButton=new CVButton();			textOnButton(cvButton,"restart");			cvButton.x=100;			cvButton.y=200;			cvButton.width=90;			cvButton.height=30;			end.addChild(cvButton);			stage.focus=cvButton;			cvButton.enable(CVEvent.SHELL);			cvButton.addEventListener(MouseEvent.CLICK, restartGame);			*/
			timer = new Timer(5000, 1);
			timer.addEventListener(TimerEvent.TIMER_COMPLETE, restartGame);
			timer.start();
		}
		//things with CVButton...
		private function textOnButton(button: CVButton, text: String): void { //places the text centered on the up state
			var doc: DisplayObjectContainer = button.upState as DisplayObjectContainer;
			var tf: TextField = doc.getChildAt(1) as TextField;
			tf.text = text;
			tf.autoSize = "center"; //places the text centered on the over state
			doc = button.overState as DisplayObjectContainer;
			tf = doc.getChildAt(1) as TextField;
			tf.text = text;
			tf.autoSize = "center"; //places the text centered on the down state
			doc = button.downState as DisplayObjectContainer;
			tf = doc.getChildAt(1) as TextField;
			tf.text = text;
			tf.autoSize = "center";
		} //make actor disappears
		private function destroyBodies(): void {
			var b2: b2Body = world.GetBodyList();
			while (b2 != null) {
				var actor: b2Actor = b2.GetUserData();
				if (actor != null) {
					if (actor.removalFlag == true) {
						this.removeChild(actor.costume);
						arrayOfEggs.splice(arrayOfEggs.indexOf(actor), 1);
						actor.destroy();
						world.DestroyBody(b2);
					}
				}
				b2 = b2.GetNext();
			}
		}
		//move the basket by key board
		//list of keys to move the basket http://www.dakmm.com/?p=272
		public function move(e: KeyboardEvent) {
			trace(e.keyCode);
			//when click left arrow
			      
			if (e.keyCode == 37) {
				basket.body.SetPosition(new b2Vec2(chicken.body.GetPosition().x - MOVE_STEP, basket.body.GetPosition().y));       
				basket.costume.scaleX = 1;      
			}
			//when click right arrow
			else if (e.keyCode == 39) {
				basket.body.SetPosition(new b2Vec2(chicken.body.GetPosition().x + MOVE_STEP, basket.body.GetPosition().y));       
				basket.costume.scaleX = -1;      
			}
			//when click space bar
			//lays lots of eggs
			else if (e.keyCode == 32) {
				createBall();
			}
			//when click on letter d
			else if (e.keyCode == 68) {
				trace(e.keyCode);
				basket.body.SetPosition(new b2Vec2(basket.body.GetPosition().x + MOVE_STEP, basket.body.GetPosition().y));
			}
			//when click on letter s
			else if (e.keyCode == 83) {
				basket.body.SetPosition(new b2Vec2(basket.body.GetPosition().x - MOVE_STEP, basket.body.GetPosition().y));
			} else {
				trace(e.keyCode);
			}    
		}
		private function restartGame(e: Event) {
			timer.stop();
			stage.focus = null;
			removeChild(end);
			missed = 0;
			got = 0;
			numGot.text = got.toString();
			numMissed.text = missed.toString();
			world = null;
			arrayOfEggs = new Array();
			createWorld(); //enableDebugDraw();
			createPins();
			addChicken();
			createGround();
			createBasket();
			this.stage.addEventListener(KeyboardEvent.KEY_DOWN, move); //trace(stage.hasEventListener(KeyboardEvent.KEY_DOWN));
			this.addEventListener(Event.ENTER_FRAME, onEnterFrame);
			addTimer();
		}        
		private function addChicken(): void { //make a new chicken instance
			      
			chicken = new Chicken(b2Utils.createBox(500 / 2 + 10, 10, 20, 10, b2Body.b2_kinematicBody, world)); //var cf:ChickenFly =new ChickenFly();
			//chicken.GetDefinition().SetUserData=cf; //trace(chicken.GetDefinition().userData); //trace(cf);
			//add child
			addChild(chicken.costume);
		}
	}
}