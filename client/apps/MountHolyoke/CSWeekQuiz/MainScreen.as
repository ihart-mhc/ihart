﻿package {	import flash.events.MouseEvent;	import ihart.event.*;	import flash.display.MovieClip;	import flash.display.DisplayObjectContainer;	import flash.text.TextField;	public class MainScreen extends MovieClip {				var quizSelectionButton : Button;		var gameSelectionButton : Button;				public function MainScreen(){			quizSelectionButton = new Button();			var doc:DisplayObjectContainer = quizSelectionButton.upState as DisplayObjectContainer;			var tf:TextField = doc.getChildAt(1) as TextField;			tf.text = "I wanna find out how energy efficient I am!";			tf.autoSize = "center";						doc = quizSelectionButton.downState as DisplayObjectContainer;			tf = doc.getChildAt(1) as TextField;			tf.text = "I wanna find out how energy efficient I am!";			tf.textColor = 0xAAAAAA;			tf.autoSize = "center";						doc = quizSelectionButton.overState as DisplayObjectContainer;			tf = doc.getChildAt(1) as TextField;			tf.text = "I wanna find out how energy efficient I am!";			tf.textColor = 0xAAAAAA;			tf.autoSize = "center";						gameSelectionButton = new Button();			doc = gameSelectionButton.upState as DisplayObjectContainer;			tf= doc.getChildAt(1) as TextField;			tf.text = "I wanna save the world!"; 			tf.autoSize = "center";						doc = gameSelectionButton.downState as DisplayObjectContainer;			tf= doc.getChildAt(1) as TextField;			tf.text = "I wanna save the world!";			tf.textColor = 0xAAAAAA;			tf.autoSize = "center";						doc = gameSelectionButton.overState as DisplayObjectContainer;			tf= doc.getChildAt(1) as TextField;			tf.text = "I wanna save the world!";			tf.textColor = 0xAAAAAA;			tf.autoSize = "center";						quizSelectionButton.x = -1 * (quizSelectionButton.width + quizSelectionButton.width/2);			quizSelectionButton.y = 100;/*			quizSelectionButton.setCVManager(MovieClip(root).cv_man);			quizSelectionButton.enable(CVEvent.SHELL);*/						gameSelectionButton.x = quizSelectionButton.width/2;			gameSelectionButton.y = 100;/*			gameSelectionButton.setCVManager(MovieClip(root).cv_man);			gameSelectionButton.enable(CVEvent.SHELL);*/						quizSelectionButton.addEventListener(MouseEvent.CLICK, quizSelectionButtonClicked);			gameSelectionButton.addEventListener(MouseEvent.CLICK, gameSelectionButtonClicked);						addChild(quizSelectionButton);			addChild(gameSelectionButton);		}				function quizSelectionButtonClicked(e:MouseEvent):void {			//Let's take a quiz!			MovieClip(root).playQuiz();		}		function gameSelectionButtonClicked(e:MouseEvent):void {			//Let's play the game...			trace("Play game!");						MovieClip(root).playGame();		}			}}/**/