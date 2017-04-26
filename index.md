## Welcome to the iHart GitHub Page!

The iHart: Interactive Hallways for Attraction and Retention in Technology project provides inexperienced programmers with the unique opportunity to develop interactive scenes and games that can be displayed on floors and walls, creating a fun and refreshing diversion from the hustle of everyday life for anyone who walks by. The project strengths lie in its intuitive development environment and its easy and inexpensive installation into the hallway. The goal of the iHart project is to attract and inspire students to pursue careers in computer science and information technology.

## How to download and install iHart:

You can download all the files necessary for installing and running iHart on you computer using the above links.

Setting up an iHart display takes two steps: running the server, then running a client application. Your computer should have a webcam available.

### Running the server
1. To run the iHart server software go to where you downloaded the project. Navigate to **server --> dist**, then go to either **mac** or **windows** depending on your operating system. Run the program called **cvServer**.
1. The server should look something like the below image.

	![iHart start screen](http://ihart-mhc.github.io/software/img/cvServer-start.png)

    The camera index slider matters if you have more than one web camera attached to a computer (for example, one that’s built in and one that’s connected via USB). If you choose the wrong index, restart iHart and try again with a different one.

1. When the program opens, the controls window will appear on top of two other windows. One shows the detected motion in black and white (white is motion), and the other shows the video feed. The motion window may also appear on top of the video window.
1. A region of interest is automatically created so that the server sends motion to the client application(s). You can also create one yourself. To do so, first right-click inside the existing blue box on the screen to remove the current area of interest. Next, click on a starting point in the video window, and drag your mouse across the window until you are satisfied, then release the mouse button. Areas of interest appear in blue; motion is yellow.

	![iHart video window with motion and areas of interest](http://ihart-mhc.github.io/software/img/video-interest-motion.png)

### Running a client app
1. Next, return to the main iHart folder and go to **client --> apps**.
1. Choose an application, and check out how to run applications on the [applications page](/applications).
