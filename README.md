# [iHart](http://ihart-mhc.github.io/)

The iHart: Interactive Hallways for Attraction and Retention in Technology project provides inexperienced programmers with the unique opportunity to develop interactive scenes and games that can be displayed on floors and walls, creating a fun and refreshing diversion from the hustle of everyday life for anyone who walks by. The project strengths lie in its intuitive development environment and its easy and inexpensive installation into the hallway. The goal of the iHart project is to attract and inspire students to pursue careers in computer science and information technology.

The iHart system consists of two parts - a server and a client. The server uses OpenCV to monitor the camera feed for motion. The client triggers CVEvents based on the information it receives from the server. The iHart applications create an instance of the client and listen to the CVEvents, which they can respond to as they would to a MouseEvent.

***

#### Installing iHart  
You can find all the necessary files for installing the iHart application on Windows or iOS in the __server__ folder.  

* __server__ - files needed for the installation of the iHart software
    * __dist__ - the iHart application exported for iOS and Windows
        * __mac__
            * __cvServer.app__ - the iHart application
            * __cvServer__ - the iHart application that runs from the terminal
        * __windows__
            * __cvServer__ - application files (do not touch unless you know what you're doing)
            * __cvServer.exe__ - the iHart application
    * __src__ - the source code for the iHart application

#### iHart Applications  
All the curently available iHart applications can be found in the __client__ folder.  

* __client__ - files needed for running iHart applications.
    * __apps__ - library of the currently available Flash and Java iHart applications
    * __library__ - the iHart event libraries for Flash and Java (do not touch unless you know what you're doing)
    * __tutorials__ - documentation of how to create and use iHart applications, plus a demo app


### iHart Documentation
Some PDF documentation can be found in the __doc__ folder. More can be found [on the iHart website](http://ihart-mhc.github.io/), under Application Development and Software Development.

There is little documentation about installing from source; the source code is located in __server__ --> __src__ and requires Python 2.7+ and OpenCV 2 for Python.
