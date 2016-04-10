#!/bin/bash
# A bash script file that rotate applications
# Make sure to keep this file in the same folder with all the application files
# By Kayla Nguyen

# an array to keep the name of applications
appArray=(Calendar Calculator Chess Messages Notes Reminders)

# print out all the items in the appArray
echo ${appArray[@]}

# bash while loop
# everytime sleep 5 seconds
while sleep 5; do
	# create a random number between 0 and 5:
 	number=$[ ( $RANDOM % 5 ) ]
 	# print out the random numer
 	echo $number
 	# a variable to hold the name of opened application
  	openedApp=${appArray[number]}
 	# print out the random app name
 	echo $openedApp
 	# open the application
 	# the “-a” flag to specify the application by name
  	open -a ${appArray[number]}; ccf
  	# if the application is ... (chess or calendar)
  	# There must be a space between if and [
  	if [ $openedApp = "Chess" ] || [ $openedApp = "Calendar" ]; then
  		# change volumn to 50%
  		osascript -e "set volume output volume 50"
  	else
  		# change volumn to 10%
  		osascript -e "set volume output volume 10"
  	fi
  	# wait for 3 seconds
  	sleep 3
  	# quit the app
  	# osascript -e 'quit app "Calendar"'
  	# kill the app
  	killall $openedApp
done