import processing.core.*; 
import processing.xml.*; 

import hypermedia.video.*; 
import processing.net.*; 
import java.io.*; 
import java.nio.ByteBuffer; 
import java.awt.Shape; 
import java.awt.Polygon; 
import interfascia.*; 
import java.awt.TextField; 
import java.awt.Rectangle; 
import java.awt.Point; 

import java.applet.*; 
import java.awt.*; 
import java.awt.image.*; 
import java.awt.event.*; 
import java.io.*; 
import java.net.*; 
import java.text.*; 
import java.util.*; 
import java.util.zip.*; 
import java.util.regex.*; 

public class CVServer extends PApplet {












/**
* GeneralServer2.0
* @author CleoSchneider drawing on work done by Audrey St. John
*
* GeneralServer2.0 combines the functionality of the original GeneralServer
* some better detection techniques implemented for detecting holes. The server
* opens a socket on the specified port and using a camera takes the difference
* between a reference shot and current background to find all "blobs" within the
* image. These blobs good be holes or solid objects. We then send the information
* out to all programs listening on specified port.
**/

/**
* Fields
**/
//We may send to types of blobs a shell or solid object
//or we may send a hole or filled object
static final int SHELL = 0;
static final int HOLE = 1;
static final int FACES=2;
static final int RESUME_DELAY = 10;

//if we want to delay sending information so that we don't
//overload the server
static final int DELAY_MAX = 0;

//minimum width of a hole if we are considering holes
int HOLE_THRESH = 75;

//if we want to include a timer of sorts for this we will use this field
boolean resumeAble = false;

//booleans to tell whether we are sending holes, shells, or both
boolean holesEnabled = false;
boolean shellsEnabled = false;
boolean facesEnabled=false;

//the count
int counter = 0;

//the server
Server myServer;

//an instance of opencv
OpenCV opencv;

//timer for resume
int elapsedTime = 0;

// width and height to be scaled to
int targetW = 800;
int targetH = 500;

//width and height of the frame
int w = 1200;
int h = 400;

//the offset of the image from the edge of the frame or other images
int imWidthOffset = 10;
int imHeightOffset = 10;

//macros for offsetting x coordinates
int DISPLACE_XHOLE = imWidthOffset + (2*(w/4));
int DISPLACE_XSHELL = imWidthOffset + w/4;
int DISPLACE_XFACE= imWidthOffset+(3*(w/4));

//the height of the space for the buttons
int buttonPanelHeight = 75;

//threshold for the image
boolean shellThresholding = false, holeThresholding = false, flipHorizontal=false;
int threshold = 208;
int threshold2 = 24;
int shellThresh = 80;

//the current starting positions for the most recent box
float selStartX;
float selStartY;

//save start and end points for the selected rectangle
ArrayList selRectStartX;
ArrayList selRectStartY;
ArrayList selRectEndX;
ArrayList selRectEndY;


//the scaled positions for the box
ArrayList scaleX;
ArrayList scaleY;

//an array for the pixels
int[] pix;

//boolean for if we have set the area of interest
boolean rectSet = false;

//the button fields
//the interfascia version of a JPanel
GUIController c;

//the buttons
IFButton resetAreas, newRefShot, setHoleThresh, quit;

//the checkboxes
IFCheckBox flipHor, hole, shell, resume, shellThreshEnable, holeThreshEnable, faces;

//how many blobs we have to send over on every tic
int numSentBlobs;


/**
* Setup
* Like a main method sets up the frame for reading images from the camera selected
**/
public void setup() {
  
   //set the size of the entire frame
   size( w+imWidthOffset, (h/2) + imHeightOffset*3 + buttonPanelHeight);
   
   //initialize the list of starting positions   
   selRectStartX = new ArrayList();
   selRectStartY = new ArrayList();
   selRectEndX = new ArrayList();
   selRectEndY = new ArrayList();
   
   //initialize the list of scaling lists
   scaleX = new ArrayList();
   scaleY = new ArrayList();
   
   // Starts a myServer on port 5204
   myServer = new Server(this, 5204); 
   
   //creates a new instance of openCV
    opencv = new OpenCV( this );
    
    //begins reading images from the camera
    //can pass width, height, and index of camera to be used
    opencv.capture((w/4)-imWidthOffset,h/2);
    opencv.cascade( OpenCV.CASCADE_FRONTALFACE_ALT );    // load the FRONTALFACE description file
    createButtons();
    
    selRectStartX.add((float)imWidthOffset);
   selRectStartY.add((float)imHeightOffset);
   selRectEndX.add((float) w/4);
   selRectEndY.add((float) h/2 + imHeightOffset);
   
      //add the width and height to the scaled arraylists 
   scaleX.add((float) targetW/Math.abs(imWidthOffset-(w/4)));
   scaleY.add((float) targetH/Math.abs(imHeightOffset-(h/2+imHeightOffset)));
}

/**
* Like the second part of the main method
* Executed line by line after the setup()
**/
public void draw() {
   setScreen();
   
   
   
   //dont fill in the shape
   noFill();
   
   //walk through the blobs and send a long string concatinated by the indices for better indexing
   StringBuffer s = new StringBuffer();
   
   //the number of blobs to be sent over
   numSentBlobs = 0;
   
   //check whether holes or shells were enabled and egin detecting them
   checkTypeEnabled(s);
   
   //if we have chosen an area of interest, maintain the bounding rectangle
   //echo the bounding rectangle in the difference frame
   drawSelectedAreas();
   
   //delay how often we send information using a counter
   if(counter<DELAY_MAX){
     counter++;
     return;
   }

   myServer.write(0);  
     
   //write the string to the server
   if(s.length() > 2){
     
     //insert the number of blobs at the beginning of the string
     s.insert(0, Integer.toString(numSentBlobs) + ":" );
     
     //filter out whether we are using a timer or not
     filterResume(s);
   }
   
   //a counter so we don't send so many things
   counter = 0;   
}

/**
* Check whether holes or shells were enabled, and if they were display the images and create the output strings
*
**/
public void checkTypeEnabled(StringBuffer s){
     //create the string for shells if they are enabled
   if(shellsEnabled){
     
     //apply appropriate filters for shells
     Blob[] shells = detectShells();
     
     //push the current coordinate system onto the matrix stack
     pushMatrix();
     
     //translate the matrix over to the difference image to the right
     translate(DISPLACE_XSHELL,imHeightOffset);
     s.append(createOutputString(shells, SHELL));
     
     //restore the previous coordinate system
     popMatrix();
   }
   
   //create the string for holes if they are enabled
   if(holesEnabled){
     
     //apply appropriate filters for holes
     Blob[] holes = detectHoles();
     
     //push the current coordinate system onto the matrix stack
     pushMatrix();
     
     //translate the matrix over to the difference image to the right
     translate(DISPLACE_XHOLE,imHeightOffset);
     s.append(createOutputString(holes, HOLE));
     
     //restore the previous coordinate system
     popMatrix();
   }
   if(facesEnabled){
     Rectangle[] faces;
     String s2;
     pushMatrix();
     
     translate(DISPLACE_XFACE,imHeightOffset);
     
     faces=detectFaces();
     
    for( int i=0; i<faces.length; i++ ) {
      
      
           //calculate the scaled coordinates for the blob
     double[] scaledInfo = calcScaled( faces[i].x, faces[i].y,faces[i].width, faces[i].height, 0 );
     
     //save the current scaled values
     double currentScaledX, currentScaledY, currentScaledWidth, currentScaledHeight;
     
     // if within bounds, then scaledInfo is not null
     if ( scaledInfo != null ){
        currentScaledX = scaledInfo[0];
        
        // for flipping
        if ( flipHorizontal )
          currentScaledX = targetW - currentScaledX;
          
        currentScaledY = scaledInfo[1];
        currentScaledWidth= scaledInfo[2];
        currentScaledHeight = scaledInfo[3];
        
        
         numSentBlobs++;
         s2=(Integer.toString(numSentBlobs-1+i) + "," + Integer.toString((int)currentScaledX) + "Y" + Integer.toString((int)currentScaledY) 
                    + "W" + Integer.toString((int)currentScaledWidth) + "H" + Integer.toString((int)currentScaledHeight) + "T" + Integer.toString( FACES ) + ";");
         if(s !=null){
           s.append(s2);
         }
      }
    }

     popMatrix();
   }
}

public Rectangle[] detectFaces(){
  
  //opencv.cascade( OpenCV.CASCADE_FRONTALFACE_ALT );    // load the FRONTALFACE description file
  opencv.read();
  
  image( opencv.image(), 0, 0 );
    
    // detect anything ressembling a FRONTALFACE
    Rectangle[] faces = opencv.detect();
    
    // draw detected face area(s)
    noFill();
    stroke(255,0,0);
    for( int i=0; i<faces.length; i++ ) {
        rect( faces[i].x, faces[i].y, faces[i].width, faces[i].height ); 
    }
    return faces;
}
/**
* setScreen
* creates the initial setup for the screen on every draw
**/
public void setScreen(){

   opencv.read();
   if ( flipHorizontal )
     opencv.flip( OpenCV.FLIP_HORIZONTAL );
   
   // image in memory 
   image( opencv.image(OpenCV.MEMORY), imWidthOffset, imHeightOffset);
   
   //take the difference between the reference shot and the current image
   opencv.absDiff();
   
   //set the threshold
   opencv.threshold( shellThresh);
   
   //put the binary image on the right hand side of the reference image
   image( opencv.image(OpenCV.GRAY), DISPLACE_XSHELL, imHeightOffset);
   
   //put another image for detecting holes so that we can see both at the same time
   image( opencv.image(OpenCV.GRAY), DISPLACE_XHOLE, imHeightOffset);  
   
     //put another image for detecting faces so that we can see both at the same time
   image( opencv.image(OpenCV.GRAY), DISPLACE_XFACE, imHeightOffset);
}


/**
* createButtons
* create all buttons for this app
**/
public void createButtons(){

    //create buttons at the bottom of the screen
    c = new GUIController(this);
   
    //put the reset button in the lower left hand corner
    resetAreas = new IFButton("Reset Areas", imWidthOffset+20, h/2 + imHeightOffset*2);
    
    //put the refShot button next to the reset button
    newRefShot = new IFButton("Ref Shot", (w/6)+imWidthOffset+20, h/2 + imHeightOffset*2); 
    
    //put the checkboxes in next to the buttons
    hole = new IFCheckBox("Enable Holes", (w/2)+(w/8)-45, h/2 + imHeightOffset*2);
    
    //update the next spot

    shell = new IFCheckBox("Enable Shells", (w/4)+(w/8)-45, h/2 + imHeightOffset*2);
    
    faces= new IFCheckBox("Enable Faces", (3*(w/4))+(w/8)-45,  h/2 + imHeightOffset*2);
    //update the next spot
    flipHor = new IFCheckBox("Flip Horizontally",  (3*(w/4))+(w/8)-45,  h/2 + imHeightOffset*6);
    
    //update the next spot
    resume = new IFCheckBox("Enable Timer", (w/6)+imWidthOffset+20, h/2 + imHeightOffset*6);
    
    shellThreshEnable = new IFCheckBox("Shell Threshold",  (w/4)+(w/8)-45, h/2 + imHeightOffset*6);
    
    holeThreshEnable = new IFCheckBox("Hole Threshold",  (w/2)+(w/8)-45, h/2 + imHeightOffset*6);
    
    //add a quit button
    quit = new IFButton("Quit", imWidthOffset+20, h/2 + imHeightOffset * 6);

    //add the buttons to the GUIController
    c.add(resetAreas);
    c.add(newRefShot);
    c.add(hole);
    c.add(shell);
    c.add(faces);
    c.add(flipHor);
    c.add(resume);
    c.add(shellThreshEnable);
    c.add(holeThreshEnable);
    c.add(quit);
    
    //add listeners to each of the components in the controller
    resetAreas.addActionListener(this);
    newRefShot.addActionListener(this);
    hole.addActionListener(this);
    shell.addActionListener(this);
    faces.addActionListener(this);
    flipHor.addActionListener(this);
    resume.addActionListener(this);
    shellThreshEnable.addActionListener(this);
    holeThreshEnable.addActionListener(this);
    quit.addActionListener(this);
}

/**
* Draw all areas in the selectedrect arraylist
**/
public void drawSelectedAreas()
{
    //walk along the arraylist
    for ( int i = 1; i < selRectStartX.size(); i++ )
    {
        // left side
          boundArea(getFloatOut(selRectStartX, i), getFloatOut(selRectStartY, i), 
              Math.abs(getFloatOut(selRectStartX, i) - getFloatOut(selRectEndX, i)), Math.abs( getFloatOut(selRectStartY, i) - getFloatOut(selRectEndY, i)));
       // middle
          boundArea(getFloatOut(selRectStartX, i) + DISPLACE_XSHELL-imWidthOffset, getFloatOut(selRectStartY, i), 
              Math.abs(getFloatOut(selRectStartX, i) - getFloatOut(selRectEndX, i)), Math.abs( getFloatOut(selRectStartY, i) - getFloatOut(selRectEndY, i)));
       // right side
          boundArea(getFloatOut(selRectStartX, i) + DISPLACE_XHOLE-imWidthOffset, getFloatOut(selRectStartY, i), 
              Math.abs(getFloatOut(selRectStartX, i) - getFloatOut(selRectEndX, i)), Math.abs( getFloatOut(selRectStartY, i) - getFloatOut(selRectEndY, i)));
        
    }
}

/**
* createOutputString
* given an array of blobs walk along and append a stringBuffer
* @return: the string ready for output
**/
public String createOutputString(Blob[] blobs, int type){
  StringBuffer bs = new StringBuffer();
  String s;
  //walk along the blobs and send them over if they are in bounds
   for( int i=0; i<blobs.length; i++ ) {
     
        //create a bounding rectangle for the blob
        createBlobRect(blobs[i]);
        
        //create the centroid
        createBlobCentroid(blobs[i]);
        
        //fill the shape
        fillBlob(blobs[i]);
        
        //check if the blob is in bounds 
        //walk along all of the areas of interest and check if the blob is contained inside
        for ( int j = 1; j < selRectStartX.size(); j++ )
        {
          s = filterTest( blobs[i], j, numSentBlobs, type );
          //if a string was returned then append the stringBuffer
          if(s !=null){
            
            //check if the blob is actually a hole
            bs.append(s);
            
            //advance the count of the number of blobs to send
            numSentBlobs++;
            if(Integer.parseInt(s.substring(s.length()-2, s.length()-1))==HOLE){
              //fill the blob that was found
              fillFollowed( blobs[i], HOLE);
            }
            else{
              //fill the blob that was found
              fillFollowed( blobs[i], SHELL);
            }
          }
        }
   }
   return bs.toString();
}

/**
* createBlobRect
* draw a rectangle around the passed blob
**/
public void createBlobRect(Blob blob){
  Rectangle bounding_rect = blob.rectangle;
  // rectangle around the blob
  noFill();
  stroke( blob.isHole ? 128 : 64 );
  rect( bounding_rect.x, bounding_rect.y, bounding_rect.width, bounding_rect.height );
}

/**
* createBlobCentroid
* draw a + at the center of the blob
**/
public void createBlobCentroid(Blob blob){
  //get the center point of the current blob        
  Point centroid = blob.centroid;
  // centroid
  stroke(0,0,255);
  line( centroid.x-5, centroid.y, centroid.x+5, centroid.y );
  line( centroid.x, centroid.y-5, centroid.x, centroid.y+5 );
  noStroke();
  fill(0,0,255);
}

/**
* fillBlob
* fill in the points of the blob with purple
**/
public void fillBlob(Blob blob){
  //get the points bounding the blob
  Point[] points = blob.points;
  
  //fill in the shape
  fill(255,0,255,64);
  stroke(255,0,255);
  
  //if there are points start a shape
  if ( points.length>0 ) {
    beginShape();
    
    //use each of the points as a vertex
    for( int j=0; j<points.length; j++ ) {
      vertex( points[j].x, points[j].y );
    }
    //end the shape
    endShape(CLOSE);
  } 
  
  //reset the stroke  
  noStroke();
  fill(255,0,255);  
}

/**
* detectHoles
* use the binary inverse filter in order to get optimal hole detection
* take the difference between the image in memory and the current image,
* convert it to grayscale, and put it through two filters
* @return: an array of blobs
**/
public Blob[] detectHoles(){
   //restore the RGB image
   opencv.restore();
   
   //take the difference between the reference shot and the current image
   opencv.absDiff(); 
   
   //convert the image to grayscale  
   opencv.convert( OpenCV.GRAY);
   
   //set the threshold
   opencv.threshold( threshold2 );
   
   //use the binary inverse to round the grayscale colors to either black or white
   opencv.threshold(threshold, 255,OpenCV.THRESH_BINARY_INV);
   
   //put the binary image on the right hand side of the reference image
   image( opencv.image(OpenCV.GRAY), DISPLACE_XHOLE, imHeightOffset);
   
   //save the pixels from the current difference in the array pix because when we ask
   //for blobs it changes the image in the opencv buffer
   pix = opencv.pixels(OpenCV.BUFFER);
   
   //get the blobs from opencv
   return opencv.blobs( 5, ((w/3)*(h/2))/3, 20, true );
}

/**
* detectShells
* take the difference between the image in memory and the current image,
* put it through the default RGB filter using threshold2
* @return: an array of blobs
**/
public Blob[] detectShells(){
   //the default set up is to deal with shell so we only need return the blobs  
   //get the blobs from opencv
   return opencv.blobs( 5, ((w/3)*(h/2))/3, 20, true );
}

/**
* ActionPerformed
* dictates what we should do when a button is clicked
**/
public void actionPerformed(GUIEvent e){
  //check which button or check box was clicked
  if( e.getSource() == resetAreas){
    
    //reset all the areas of interest
    rectSet = false;
    
    //reset the initial area
    selRectStartX.clear();// = 10;
    selRectStartY.clear();// = 10;
    selRectEndX.clear();// = w+10;
    selRectEndY.clear();// = h+10;
  }
  
  if( e.getSource() == newRefShot){
    //take a new reference shot
    opencv.remember();
  }
  
  if( e.getSource() == hole){
    //if the checkbox is selected then set the program to look for holes
    holesEnabled = !holesEnabled;
    println("sending holes: " + Boolean.toString(holesEnabled));
  }
  
  if( e.getSource() == shell){
    shellsEnabled = !shellsEnabled;
    println("sending shells: " + Boolean.toString(shellsEnabled));
  }
    if( e.getSource() == faces){
    facesEnabled = !facesEnabled;
    println("sending faces: " + Boolean.toString(facesEnabled));
  }
  if( e.getSource() == flipHor){
    //if the threshEnable is checked then we may adjust the threshold
    flipHorizontal = !flipHorizontal;
    println("flip horizontal: " + Boolean.toString(flipHorizontal));
  }
  
  
  if( e.getSource() == resume){
    //if the checkbox is selected then set the program to start the timer
    resumeAble = !resumeAble;
    println("resume: " + Boolean.toString(resumeAble));
  }
  
  if( e.getSource() == shellThreshEnable){
    //if the threshEnable is checked then we may adjust the threshold
    shellThresholding = !shellThresholding;
    println("thresholding: " + Boolean.toString(shellThresholding));
  }
  
  if( e.getSource() == holeThreshEnable){
    //if the threshEnable is checked then we may adjust the threshold
    holeThresholding = !holeThresholding;
    println("thresholding: " + Boolean.toString(holeThresholding));
  }
  
  if(e.getSource() == quit){
    //if quit is clicked then stop the program
    stop();
  }
}

/**
* Filter out whether we are using the resume or not
**/
public void filterResume(StringBuffer s){
  //if we are using the timer then deal with the timer and insert the signifier
  if(resumeAble){
   if(elapsedTime>=RESUME_DELAY){
      //insert a signifier for the RESUME
      s.insert(0, "R");
      elapsedTime = 0;
    }
    else{
      //there's nothing of interest
      if(elapsedTime<RESUME_DELAY+2){
        //advance the timer
        elapsedTime++;
      }
    }
  }
  
  //write the blobs of interest to the server
  myServer.write(s.toString() + "\n");
  println(s.toString() + "\n");
}

/**
* FilterTest 
* Test if the the blob is above the threshold for a hole
**/
public String filterTest( Blob b, int indexOfInterest, int numBlobbers, int type ){
   //calculate the scaled coordinates for the blob
   double[] scaledInfo = calcScaled( b.centroid.x, b.centroid.y, b.rectangle.width, b.rectangle.height, indexOfInterest );
   
   //save the current scaled values
   double currentScaledX, currentScaledY, currentScaledWidth, currentScaledHeight;
   
   // if within bounds, then scaledInfo is not null
   if ( scaledInfo != null ){
      currentScaledX = scaledInfo[0];
      currentScaledY = scaledInfo[1];
      currentScaledWidth= scaledInfo[2];
      currentScaledHeight = scaledInfo[3];
      
      //if it's a hole within the right threshold return the string
      //if it is a shell then append and return the string regardless of whether it is white
      if( (type == HOLE && isHole(b)) || (type == SHELL && !b.isHole) ){
        return Integer.toString(numBlobbers) + "," + Integer.toString((int)currentScaledX) + "Y" + Integer.toString((int)currentScaledY) 
                  + "W" + Integer.toString((int)currentScaledWidth) + "H" + Integer.toString((int)currentScaledHeight) + "T" + Integer.toString( type ) 
				// added ASJ for area of interest (-1 since indices seem to start at 1)
				+ "I" + Integer.toString(indexOfInterest-1) + ";";
      }
      
   }
   return null;
}


/** 
 * Calculates scaled x, y, w, h for given x, y, w, h with respect to area of interest at
 * index. If the x, y do not fall within bounds of that area of interest, returns null
 **/
public double[] calcScaled( float x, float y, float wid, float hei, int areaOfInterestIndex )
{
  //scale the rectangle around the blob according to the size of the area of interest
  if((x > getFloatOut( selRectStartX, areaOfInterestIndex )) && (x < getFloatOut( selRectEndX, areaOfInterestIndex )) 
            && (y > getFloatOut( selRectStartY, areaOfInterestIndex )) && (y < getFloatOut( selRectEndY, areaOfInterestIndex )) )
     {      
          //scale the x and y coordinates      
          double currentScaledX = ((x - getFloatOut( selRectStartX, areaOfInterestIndex ))*getFloatOut( scaleX, areaOfInterestIndex )); 
          double currentScaledY = ((y - getFloatOut( selRectStartY, areaOfInterestIndex ))*getFloatOut( scaleY, areaOfInterestIndex )); 
          
          //scale the width and height
          double currentScaledWidth = wid*getFloatOut( scaleX, areaOfInterestIndex );
          double currentScaledHeight = hei*getFloatOut( scaleY, areaOfInterestIndex );
          
          //put the newly scaled values into an array and return that array
          double[] info = {currentScaledX, currentScaledY, currentScaledWidth, currentScaledHeight};
          return info;
     }
  else
  {
    // outside area
    return null;
  }
}

/**
* GetFloatOut takes the double in the array list and changes it to a float 
**/
public float getFloatOut( ArrayList list, int index )
{
  return ((Float)list.get(index)).floatValue();
}

/**
* Draw the bounding rectangle for the area of interest
**/
public void boundArea(float start,float end, float w, float h){
  noFill();
  stroke(255, 0, 0);
  rect(start, end, w, h);
}

/**
* Fill the blob that is being followed
**/
public void fillFollowed(Blob b, int type){
  println("following" + " type: " + type );
  //get the points bounding the blob
  Point[] points = b.points;
  
  //if we are dealing with a hole we want to mark it green
  //otherwise we will mark it blue
  if(type == HOLE){
    println("following holes");
    //fill in the shape
    fill(0,255,0,64);
    stroke(0,255,0);
    //if there are points start a shape
    if ( points.length>0 ) {
      beginShape();
      //use each of the points as a vertex
      for( int j=0; j<points.length; j++ ) {
        vertex( points[j].x - DISPLACE_XHOLE, points[j].y );
        println("orig x: " + points[j].x + "\ntranslated x: " + (points[j].x-DISPLACE_XHOLE));
      }
      //end the shape
      endShape(CLOSE);
    } 
    //reset the stroke  
    noStroke();
    fill(0,255,0);
  }
  else{
    //fill in the shape
    fill(0,0,255,64);
    stroke(0,0,255);
    //if there are points start a shape
    if ( points.length>0 ) {
      beginShape();
      //use each of the points as a vertex
      for( int j=0; j<points.length; j++ ) {
        vertex( points[j].x - DISPLACE_XSHELL, points[j].y );
      }
      //end the shape
      endShape(CLOSE);
    } 
    //reset the stroke  
    noStroke();
    fill(0,0,255);
  }
}

/**
* findIndex
* Given an x and y coordinate find the one dimensional index into an array
* @param: i = the rows (y coors), j = the cols (x coors)
**/
public int findIndex(int i, int j){
  return i*((w/4)-imWidthOffset) + j;
}

/**
* createPolygon
* given a blob, return the polygon contained inside, so that we may check for insideness
**/
public Polygon createPolygon(Blob blob){
  
  //an array of ints for all the x's
  int[] all_x = new int[blob.points.length];
  int[] all_y = new int[blob.points.length];
  
  //a polygon to test for insideness
  Polygon p;
  
  //walk along the blobs, create a polygon for each and check if the click is contained in the blob
  //pass the blob along to get the average color
  for(int i = 0; i< blob.points.length; i++){
    //put the current point into our array 
    all_x[i] = blob.points[i].x;
    all_y[i] = blob.points[i].y;
  }
  //create a new polygon
  return new Polygon(all_x, all_y, blob.points.length);
}


/**
* isWhite uses a polygon to test if the inside of the blob is white or not
**/
public boolean isWhite(Blob blob, Polygon p, int[] pix){
  
  //get the starting coordinate of the blob passed
  int startX = blob.rectangle.x;
  int startY = blob.rectangle.y;

  //walk along all of the points in the bounding rectangle
  //if the point is in the polygon then add it to the average color
  for(int j = startY; j<startY + blob.rectangle.height; j++){
     for(int k = startX; k<startX + blob.rectangle.width; k++){
        //if the polygon contains the point, then add it to the average color
        if(p.inside(k, j)){
           //check if the pixel is white or not
           if(( red(pix[findIndex(j, k)]) != 255) && ( red(pix[findIndex(j, k)]) != 255)
            && ( red(pix[findIndex(j, k)]) != 255) )
              return false;
           
        }
     } 
  }
  //the polygon is white meaning it is a hole
  return true;
}

/**
* Set the starting coordinates for the bounding rectangle
**/
public void mousePressed(){
  if(!holeThresholding && !shellThresholding && pointBtw(imWidthOffset, imWidthOffset+w/2, imHeightOffset, imHeightOffset+h/2, mouseX, mouseY)){
    selStartX = mouseX;
    selStartY = mouseY;
    rectSet = true;
  }
}

/**
* On release set the boolean for area of interest so we may choose a threshold
* draw the bounding rectangle
**/
public void mouseReleased(){
  //only draw the rectangle representing area of interest if it is within the reference frame
  //not the difference frame
 if(!holeThresholding && !shellThresholding && rectSet && pointBtw(imWidthOffset, imWidthOffset + w/2, imHeightOffset, imHeightOffset + h/2, selStartX, selStartY) && pointBtw(imWidthOffset, imWidthOffset + w/2, imHeightOffset, imHeightOffset + h/2, mouseX, mouseY)){
   rectSet = false;
  addAreaOfInterest( selStartX, selStartY, mouseX, mouseY );
 } 
}

/**
* MouseDragged
* If we have no area of interest, create one
* Otherwise we are adjusting the threshold
**/
public void mouseDragged() {
   //a boolean to hold if either was thresholding
   boolean thresh = false;
   
   //set a new hole threshold for the image depending on the light
   if(holeThresholding){
     threshold = PApplet.parseInt( map(mouseX,0,width,0,255) );
     threshold2 = PApplet.parseInt( map(mouseY,0,height,0,255) );
     println("holeThresh:" + threshold2);
     thresh = true;
   }
   //set a new shell threshold for the image depending on the light
   if(shellThresholding){
     shellThresh = PApplet.parseInt( map(mouseY,0,height,0,255) );
     thresh = true;
   }
   
   if(!thresh && pointBtw(imWidthOffset, imWidthOffset + w/2, imHeightOffset, imHeightOffset + h/2, selStartX, selStartY) && pointBtw(imWidthOffset, imWidthOffset + w/2, imHeightOffset, imHeightOffset + h/2, mouseX, mouseY)){
     boundArea(selStartX, selStartY, Math.abs(selStartX - mouseX), Math.abs(selStartY - mouseY));
   }
}

/**
* Point lies between
* checks if a point lies within a rectangle
* the rectangle must be entered left side first, then right
* then top, then bottom
**/
public boolean pointBtw(double xLeft, double xRight, double yTop, double yBottom, double pointX, double pointY){
  //checks the parameters and returns true if the point lies between the sides
  if(pointX>=xLeft && pointX<=xRight && pointY>=yTop && pointY<=yBottom){
    println("point found between returning true");
   return true; 
  }
      println("point not found between returning false");
  return false;
}

/**
* Add an area of interest to the scene
**/
public void addAreaOfInterest( float startX, float startY, float endX, float endY )
{
   //bound new area
   boundArea(startX, startY, Math.abs(startX - endX), Math.abs(startY - endY));
   //add the coordinates to the arraylist
   selRectStartX.add( startX );
   selRectStartY.add( startY );
   selRectEndX.add( endX );
   selRectEndY.add( endY );
   //add the width and height to the scaled arraylists 
   scaleX.add( targetW/Math.abs(startX - endX) );
   scaleY.add( targetH/Math.abs(startY - endY) );

}

/**
* Check if the blob provided is a hole
**/
public boolean isHole( Blob b )
{
  return isWhite(b, createPolygon(b), pix);
}

public void stop() {
    opencv.stop();
    super.stop();
    System.exit(0);
}

  static public void main(String args[]) {
    PApplet.main(new String[] { "--bgcolor=#FFFFFF", "CVServer" });
  }
}
