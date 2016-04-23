### iHart Beats / Sounds

This is an interactive scene created for iHart. This application plays sounds when motion is detected.

#### Files included
* __iHartBeats.swf__, __iHartSounds.app__, __iHartSounds.exe__ - the exported application
* __README.md__
* __sounds.xml__ - file telling the application which sounds to play
* __soundFiles/__ - folder of sounds to play

#### How to run the application  
1. Make sure that the iHart program is running on your computer.
2. Check that the camera is working and that you have specified an appropriate interest area.
2. Add whatever sounds you want to play to the soundFiles folder.
2. In the sounds.xml file, change each sound tag to one of the sounds you would like to play. For example, to play the "Footloose.mp3" sound in the soundFiles folder, add `<sound>Footloose.mp3</sound>` to the file after the `<sounds>` tag and before the closing `</sounds>` tag.
3. To run the application open the iHartBeats.swf file.
4. As you move in front of the camera, you should hear a randomly-chosen sound from the sounds you indicated in the file.

If the iHartBeats.swf file is not working, you might need to re-export the application, or try with the .app or .exe versions (on OS X or Windows respectively).

#### Versions  
** iHartSounds v1.0.0**  
