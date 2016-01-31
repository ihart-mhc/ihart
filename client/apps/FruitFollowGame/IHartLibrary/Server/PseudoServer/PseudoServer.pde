import processing.net.*;

/**
* Server just to connect 
* the two flash sockets
**/

/**
* Fields
**/
Server myServer;
int val = 0;

/**
* Setup
**/
void setup(){
  // Starts a myServer on port 5204
  myServer = new Server(this, 5204);
}

void draw(){
     // Get the next available client
  Client thisClient = myServer.available();
  // If the client is not null, and says something, display what it said
  if (thisClient !=null) {
    String whatClientSaid = thisClient.readString();
    if (whatClientSaid != null) {
      println(thisClient.ip() + ": " + whatClientSaid);
      myServer.write( 0 );
      myServer.write( whatClientSaid );
    } 
  } 
}
