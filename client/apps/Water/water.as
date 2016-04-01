package ihart.event {
    import flash.events.*;
    import flash.net.*;

    public class CVManager extends EventDispatcher {

        private var hostName:String;
        private var port:uint;
        private var socket:XMLSocket;
        private var regionOfInterest:int;
        private var shellData:Array;
        private var holeData:Array;
        private var faceData:Array;
        private var eventData:Array;

        public function CVManager(_arg1:String, _arg2:uint, _arg3:int=0){
            trace("CVManager constructor.");
            this.hostName = _arg1;
            this.port = _arg2;
            this.regionOfInterest = _arg3;
            this.socket = new XMLSocket();
            this.configureListeners(this.socket);
            if (((_arg1) && (_arg2))){
                this.socket.connect(_arg1, _arg2);
            };
        }
        private function configureListeners(_arg1:IEventDispatcher):void{
            trace("in configureListeners.");
            _arg1.addEventListener(DataEvent.DATA, this.dataHandler);
            _arg1.addEventListener(Event.CLOSE, this.closeHandler);
            _arg1.addEventListener(Event.CONNECT, this.connectHandler);
            _arg1.addEventListener(IOErrorEvent.IO_ERROR, this.ioErrorHandler);
            _arg1.addEventListener(ProgressEvent.PROGRESS, this.progressHandler);
            _arg1.addEventListener(SecurityErrorEvent.SECURITY_ERROR, this.securityErrorHandler);
        }
        private function dataHandler(_arg1:DataEvent):void{
            var _local3:Blob;
            var _local2:Boolean;
            this.shellData = new Array();
            this.holeData = new Array();
            this.faceData = new Array();
            this.eventData = new Array();
            if (_arg1.data.indexOf("R") == 0){
                _local2 = true;
                _arg1.data = _arg1.data.substring(1, _arg1.data.length);
            };
            var _local4:int = _arg1.data.indexOf(":");
            var _local5:int = new Number(_arg1.data.substring(0, _local4));
            var _local6:String = _arg1.data;
            var _local7:int = this.findSpecificInterestArea(this.regionOfInterest, _local6);
            var _local8:int = this.findNextAreaIndex((_local7 + 2), _local6);
            if (_local7 < 0){
                return;
            };
            if (_local8 < _local7){
                _local8 = _local6.length;
            };
            var _local9:int = Number(_local6.substr(_local7, 1));
            this.parseArea(_local7, _local8, _local6, _local9);
            this.eventData = new Array(this.shellData, this.holeData, this.faceData);
            this.dispatchEvents(this.shellData.length, this.holeData.length, this.faceData.length, _local5, this.eventData, _local2);
        }
        private function parseArea(_arg1:int, _arg2:int, _arg3:String, _arg4:int):void{
            this.parseItems(_arg1, _arg2, _arg3, "Shells:", true, _arg4);
            this.parseItems(_arg1, _arg2, _arg3, "Faces:", false, _arg4);
        }
        private function parseItems(_arg1:int, _arg2:int, _arg3:String, _arg4:String, _arg5:Boolean, _arg6:int):void{
            var _local12:Blob;
            var _local7:int = _arg3.indexOf(_arg4, _arg1);
            if (_local7 < 0){
                return;
            };
            var _local8:int = (_local7 + _arg4.length);
            if (_local7 > _arg2){
                return;
            };
            var _local9 = "";
            if (_arg5){
                trace("in parseItems. 6");
                _local9 = "shell";
            } else {
                trace("in parseItems. 7");
                _local9 = "face";
            };
            var _local10:int = this.findEndOfCurrentSection(_arg1, _arg3);
            if ((((_local10 < _arg2)) && ((_local10 > 0)))){
                _arg2 = _local10;
            };
            var _local11:int = _arg3.indexOf(" ", _local7);
            while (_local8 < _arg2) {
                _local12 = this.parseItem(_local8, _local11, _arg3, _local9);
                _local8 = (_local11 + 1);
                _local11 = _arg3.indexOf(" ", _local8);
                if (_local12 != null){
                    if (_arg5){
                        this.shellData.push(_local12);
                    } else {
                        this.faceData.push(_local12);
                    };
                };
            };
        }
        private function parseItem(_arg1:int, _arg2:int, _arg3:String, _arg4:String):Blob{
            var _local5:Blob = new Blob(_arg4, -1, -1, -1, -1, -1);
            var _local6:Array = new Array(4);
            var _local7:int;
            var _local8:int;
            var _local9:int = _arg1;
            var _local10:int = (_arg3.indexOf(";", _arg1) + 1);
            if (_local10 < 0){
            };
            while ((((((_local9 < _arg2)) && ((_local9 < _local10)))) && ((_local7 < _local6.length)))) {
                _local8 = int(Number(_arg3.substring(_local9, (_local10 - 1))));
                var _temp1 = _local7;
                _local7 = (_local7 + 1);
                var _local11 = _temp1;
                _local6[_local11] = _local8;
                _local9 = _local10;
                _local10 = (_arg3.indexOf(";", _local10) + 1);
                if (_local10 < 0){
                    _local10 = _arg2;
                };
            };
            if (_local7 != 4){
                return (null);
            };
            _local5.setX(_local6[0]);
            _local5.setY(_local6[1]);
            _local5.setWidth(_local6[2]);
            _local5.setHeight(_local6[3]);
            return (_local5);
        }
        private function findEndOfCurrentSection(_arg1:int, _arg2:String):int{
            return (_arg2.indexOf("]", _arg1));
        }
        private function findNextAreaIndex(_arg1:int, _arg2:String):int{
            if (_arg1 < 0){
                return (-1);
            };
            var _local3:int = _arg2.indexOf("|", _arg1);
            if (_local3 < 1){
                return (_local3);
            };
            return ((_local3 - 1));
        }
        private function findSpecificInterestArea(_arg1:int, _arg2:String):int{
            var _local3 = (_arg1 + "|");
            return (_arg2.indexOf(_local3));
        }
        private function findKeyWordPosition(_arg1:String, _arg2:String, _arg3:int, _arg4:DataEvent):String{
            var _local5:int = (_arg4.data.indexOf(_arg1, (_arg3 + 1)) + 1);
            var _local6:int = _arg4.data.indexOf(_arg2, (_arg3 + 1));
            var _local7:String = _arg4.data.substring(_local5, _local6);
            return (_local7);
        }
        private function dispatchEvents(_arg1:int, _arg2:int, _arg3:int, _arg4:int, _arg5:Array, _arg6:Boolean):void{
            var _local7:CVEventData = new CVEventData(_arg5);
            if (_arg1 > 0){
                dispatchEvent(new CVEvent(CVEvent.SHELL, _local7, _arg6));
            };
            if (_arg2 > 0){
                dispatchEvent(new CVEvent(CVEvent.HOLE, _local7, _arg6));
            };
            if (_arg3 > 0){
                dispatchEvent(new CVEvent(CVEvent.FACE, _local7, _arg6));
            };
            if (_arg4 > 0){
                dispatchEvent(new CVEvent(CVEvent.ALL_BLOBS, _local7, _arg6));
            };
        }
        private function closeHandler(_arg1:Event):void{
            trace(("closeHandler: " + _arg1));
        }
        private function connectHandler(_arg1:Event):void{
            trace(("connectHandler: " + _arg1));
        }
        private function ioErrorHandler(_arg1:IOErrorEvent):void{
            trace(("ioErrorHandler: " + _arg1));
        }
        private function progressHandler(_arg1:ProgressEvent):void{
            trace(((("progressHandler loaded:" + _arg1.bytesLoaded) + " total: ") + _arg1.bytesTotal));
        }
        private function securityErrorHandler(_arg1:SecurityErrorEvent):void{
            trace(("securityErrorHandler: " + _arg1));
        }

    }
}//package ihart.event 
﻿package ihart.event {

    public class Blob {

        private var xCoor:Number;
        private var yCoor:Number;
        private var bWidth:Number;
        private var bHeight:Number;
        private var type:String;
        private var roi:int;

        public function Blob(_arg1:String, _arg2:Number, _arg3:Number, _arg4:Number, _arg5:Number, _arg6:int){
            this.xCoor = _arg2;
            this.yCoor = _arg3;
            this.bWidth = _arg4;
            this.bHeight = _arg5;
            this.type = _arg1;
            this.roi = _arg6;
        }
        public function getROI():int{
            return (this.roi);
        }
        public function getX():Number{
            return (this.xCoor);
        }
        public function getY():Number{
            return (this.yCoor);
        }
        public function getWidth():Number{
            return (this.bWidth);
        }
        public function getHeight():Number{
            return (this.bHeight);
        }
        public function getType():String{
            return (this.type);
        }
        public function setX(_arg1:int):void{
            this.xCoor = _arg1;
        }
        public function setY(_arg1:int):void{
            this.yCoor = _arg1;
        }
        public function setWidth(_arg1:int):void{
            this.bWidth = _arg1;
        }
        public function setHeight(_arg1:int):void{
            this.bHeight = _arg1;
        }

    }
}//package ihart.event 
﻿package ihart.event {
    import flash.events.*;

    public class CVEventData {

        private var eventData:Array;
        private var blob:Blob;

        public function CVEventData(_arg1:Array){
            this.eventData = _arg1;
        }
        public function getX(_arg1:String, _arg2:int):Number{
            this.blob = this.getBlob(_arg1, _arg2);
            return (this.blob.getX());
        }
        public function getY(_arg1:String, _arg2:int):Number{
            this.blob = this.getBlob(_arg1, _arg2);
            return (this.blob.getY());
        }
        public function getWidth(_arg1:String, _arg2:int):Number{
            this.blob = this.getBlob(_arg1, _arg2);
            return (this.blob.getWidth());
        }
        public function getHeight(_arg1:String, _arg2:int):Number{
            this.blob = this.getBlob(_arg1, _arg2);
            return (this.blob.getHeight());
        }
        public function getNumBlobs():int{
            return (this.getNum(CVEvent.ALL_BLOBS));
        }
        public function getNum(_arg1:String):int{
            if (_arg1 == CVEvent.ALL_BLOBS){
                return (((this.eventData[0].length + this.eventData[1].length) + this.eventData[2].length));
            };
            if ((((((_arg1 == CVEvent.SHELL)) || ((_arg1 == CVEvent.HOLE)))) || ((_arg1 == CVEvent.FACE)))){
                return (this.eventData[CVEvent.getIntType(_arg1)].length);
            };
            return (-1);
        }
        public function getBlob(_arg1:String, _arg2:int):Blob{
            if ((((_arg1 == CVEvent.ALL_BLOBS)) && ((_arg2 < ((this.eventData[0].length + this.eventData[1].length) + this.eventData[2].length))))){
                if (_arg2 >= this.eventData[0].length){
                    if (_arg2 >= (this.eventData[0].length + this.eventData[1].length)){
                        return (this.eventData[2][((_arg2 - this.eventData[0].length) - this.eventData[1].length)]);
                    };
                    return (this.eventData[1][(_arg2 - this.eventData[0].length)]);
                };
                return (this.eventData[0][_arg2]);
            };
            if ((((((_arg1 == CVEvent.SHELL)) || ((_arg1 == CVEvent.HOLE)))) || ((_arg1 == CVEvent.FACE)))){
                return (this.eventData[CVEvent.getIntType(_arg1)][_arg2]);
            };
            return (null);
        }

    }
}//package ihart.event 
﻿package ihart.event {
    import flash.events.*;

    public class CVEvent extends Event {

        public static const SHELL_INT:int = 0;
        public static const HOLE_INT:int = 1;
        public static const FACE_INT:int = 2;
        public static const ALL_BLOBS_INT:int = -1;
        public static const EVENT_TYPES:Array = ["shell", "hole", "face"];
        public static const SHELL:String = EVENT_TYPES[SHELL_INT];
        public static const HOLE:String = EVENT_TYPES[HOLE_INT];
        public static const FACE:String = EVENT_TYPES[FACE_INT];
        public static const ALL_BLOBS:String = "all blobs";

        private var cvData:CVEventData;
        private var resuming:Boolean;

        public function CVEvent(_arg1:String, _arg2:CVEventData, _arg3:Boolean, _arg4:Boolean=false, _arg5:Boolean=false){
            super(_arg1, _arg4, _arg5);
            this.cvData = _arg2;
            this.resuming = _arg3;
        }
        public static function getStringType(_arg1:int):String{
            if (_arg1 == CVEvent.ALL_BLOBS_INT){
                return ("all blobs");
            };
            if ((((_arg1 >= 0)) && ((_arg1 < EVENT_TYPES.length)))){
                return (EVENT_TYPES[_arg1]);
            };
            return ("");
        }
        public static function getIntType(_arg1:String):int{
            var _local2:int;
            if (_arg1 == CVEvent.ALL_BLOBS){
                return (CVEvent.ALL_BLOBS_INT);
            };
            _local2 = 0;
            while (_local2 < EVENT_TYPES.length) {
                if (EVENT_TYPES[_local2] == _arg1){
                    return (_local2);
                };
                _local2++;
            };
            return (-10);
        }

        override public function clone():Event{
            return (new CVEvent(type, this.cvData, bubbles, cancelable));
        }
        override public function toString():String{
            return (((((("Type = " + type) + ", Bubbles = ") + bubbles) + ", Cancelable = ") + cancelable));
        }
        public function getX(_arg1:int):Number{
            return (this.cvData.getX(type, _arg1));
        }
        public function getY(_arg1:int):Number{
            return (this.cvData.getY(type, _arg1));
        }
        public function getWidth(_arg1:int):Number{
            return (this.cvData.getWidth(type, _arg1));
        }
        public function getHeight(_arg1:int):Number{
            return (this.cvData.getHeight(type, _arg1));
        }
        public function getNumBlobs():int{
            return (this.cvData.getNum(type));
        }
        public function getBlob(_arg1:int):Blob{
            return (this.cvData.getBlob(type, _arg1));
        }
        public function isResuming():Boolean{
            return (this.resuming);
        }

    }
}//package ihart.event 
﻿package {
    import flash.display.*;
    import flash.events.*;
    import ihart.event.*;
    import flash.net.*;
    import flash.utils.*;
    import flash.media.*;

    public class Ripple extends Sprite {

        private var myRippler:Rippler;
        var rippleTarget:Bitmap;
        private var timerSound:Timer;
        private var hostName:String = "localhost";
        private var port:uint = 5204;
        private var cvManager:CVManager;
        private var rippleSound:Sound;
        private var soundChannel:SoundChannel;
        private var delay:int = 3500;
        private var repeat:int = 1;
        private var playingSound:Boolean = false;

        public function Ripple(){
            this.rippleSound = new Sound(new URLRequest("Sound/bubbling.mp3"));
            super();
            var _local1:BitmapData = new BitmapData(640, 480, false, 0);
            var _local2:toRipple = new toRipple();
            var _local3:Timer = new Timer(150);
            _local3.start();
            _local1.draw(_local2);
            this.rippleTarget = new Bitmap(_local1);
            addChild(this.rippleTarget);
            this.myRippler = new Rippler(this.rippleTarget, 20, 5, 5);
            stage.addEventListener(MouseEvent.MOUSE_MOVE, this.onMouseMoveTriggered);
            _local3.addEventListener(TimerEvent.TIMER, this.onTimerTriggered);
            this.cvManager = new CVManager(this.hostName, this.port);
            this.cvManager.addEventListener(CVEvent.SHELL, this.getData);
            _local3 = new Timer(this.delay, this.repeat);
            _local3.addEventListener(TimerEvent.TIMER_COMPLETE, this.timerCComplete);
        }
        public function getData(_arg1:CVEvent):void{
            var _local3:Number;
            var _local4:Number;
            trace("getting data ");
            var _local2:int = _arg1.getNumBlobs();
            var _local5:int;
            while (_local5 < _local2) {
                _local3 = _arg1.getX(_local5);
                _local4 = _arg1.getY(_local5);
                this.soundChannel = this.rippleSound.play();
                this.playingSound = true;
                this.timerSound.start();
                this.myRippler.drawRipple(_local3, _local4, 20, 1);
                _local5++;
            };
        }
        private function onMouseMoveTriggered(_arg1:MouseEvent):void{
            this.myRippler.drawRipple(this.rippleTarget.mouseX, this.rippleTarget.mouseY, 20, 1);
        }
        private function onTimerTriggered(_arg1:TimerEvent):void{
            var _local2:Number = (Math.random() * 840);
            var _local3:Number = (Math.random() * 680);
        }
        public function timerCComplete(_arg1:TimerEvent):void{
            trace("TIMER C COMPLETE");
            this.playingSound = false;
        }

    }
}//package 
﻿package {
    import flash.display.*;

    public dynamic class toRipple extends MovieClip {

    }
}//package 
﻿package {
    import flash.display.*;
    import flash.events.*;
    import flash.geom.*;
    import flash.filters.*;

    public class Rippler {

        private var originOfRipple:Point;
        private var filter:DisplacementMapFilter;
        private var expandRipples:ConvolutionFilter;
        private var sourceOfRipples:DisplayObject;
        private var firstBuffer:BitmapData;
        private var secondBuffer:BitmapData;
        private var finalBitmap:BitmapData;
        private var transformColor:ColorTransform;
        private var matrix:Matrix;
        private var invertedXScale:Number;
        private var invertedYScale:Number;
        private var createRectangle:Rectangle;
        private var drawRectangle:Rectangle;

        public function Rippler(_arg1:DisplayObject, _arg2:Number, _arg3:Number=2, _arg4:Number=2){
            var _local5:Number;
            var _local6:Number;
            this.originOfRipple = new Point();
            super();
            this.sourceOfRipples = _arg1;
            this.invertedXScale = (1 / _arg3);
            this.invertedYScale = (1 / _arg4);
            this.firstBuffer = new BitmapData((_arg1.width * this.invertedXScale), (_arg1.height * this.invertedYScale), false, 0);
            this.secondBuffer = new BitmapData(this.firstBuffer.width, this.firstBuffer.height, false, 0);
            this.finalBitmap = new BitmapData(_arg1.width, _arg1.height, false, 0x7F7F7F);
            _local5 = (this.finalBitmap.width / this.firstBuffer.width);
            _local6 = (this.finalBitmap.height / this.firstBuffer.height);
            this.createRectangle = new Rectangle(0, 0, this.firstBuffer.width, this.firstBuffer.height);
            this.drawRectangle = new Rectangle();
            this.filter = new DisplacementMapFilter(this.finalBitmap, this.originOfRipple, BitmapDataChannel.BLUE, BitmapDataChannel.BLUE, _arg2, _arg2, "wrap");
            this.sourceOfRipples.filters = [this.filter];
            this.sourceOfRipples.addEventListener(Event.ENTER_FRAME, this.handleEnterFrame);
            this.expandRipples = new ConvolutionFilter(3, 3, [0.5, 1, 0.5, 1, 0, 1, 0.5, 1, 0.5], 3);
            this.transformColor = new ColorTransform(1, 1, 1, 1, 128, 128, 128);
            this.matrix = new Matrix(_local5, 0, 0, _local6);
        }
        public function drawRipple(_arg1:int, _arg2:int, _arg3:int, _arg4:Number):void{
            var _local5 = (_arg3 >> 1);
            var _local6:int = (((_arg4 * 0xFF) & 0xFF) * _arg4);
            this.drawRectangle.x = ((-(_local5) + _arg1) * this.invertedXScale);
            this.drawRectangle.y = ((-(_local5) + _arg2) * this.invertedXScale);
            this.drawRectangle.width = (_arg3 * this.invertedXScale);
            this.drawRectangle.height = (_arg3 * this.invertedYScale);
            this.firstBuffer.fillRect(this.drawRectangle, _local6);
        }
        public function getRippleImage():BitmapData{
            return (this.finalBitmap);
        }
        public function destroy():void{
            this.sourceOfRipples.removeEventListener(Event.ENTER_FRAME, this.handleEnterFrame);
            this.firstBuffer.dispose();
            this.secondBuffer.dispose();
            this.finalBitmap.dispose();
        }
        private function handleEnterFrame(_arg1:Event):void{
            var _local2:BitmapData = this.secondBuffer.clone();
            this.secondBuffer.applyFilter(this.firstBuffer, this.createRectangle, this.originOfRipple, this.expandRipples);
            this.secondBuffer.draw(_local2, null, null, BlendMode.SUBTRACT, null, false);
            this.finalBitmap.draw(this.secondBuffer, this.matrix, this.transformColor, null, null, true);
            this.filter.mapBitmap = this.finalBitmap;
            this.sourceOfRipples.filters = [this.filter];
            _local2.dispose();
            this.switchBuffers();
        }
        private function switchBuffers():void{
            var _local1:BitmapData;
            _local1 = this.firstBuffer;
            this.firstBuffer = this.secondBuffer;
            this.secondBuffer = _local1;
        }

    }
}//package