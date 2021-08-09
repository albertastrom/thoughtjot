# ThoughtJot

ThoughtJot is a chrome extension and web app used to take convenient notes of where information is coming from. It stores this information in a database where Jots can always be accessed. 

## Getting Set Up
ThoughtJot is comprised of a Flask web application built in VSCode and a Chrome Extension also built in VSCode.

### Flask App
To install the flask app, paste the files from the "ThoughtJot" folder into a new directory from which the app will be run. To run the app, importing the libraries used in the project along with having the Python 3.9.6 or later installed is necessary. Once python is installed from `www.python.org`, libraries can be installed. 

Set up a virtual environnement in VSCode. On macOS and Linux use `python3 -m venv .venv` and on Windows use `python -m venv .venv`

In the directory's integrated terminal, run `pip install -r requirements.txt`.

Now, running the command `flask run` in the terminal will launch the web application and allow the extension to begin sending data. 

### Chrome Extension
To use the chrome extension, install the latest version of chrome. Open chrome, enter the settings, and click "Extensions" on the left side. Toggle the developer tools on mode on. Select "Load unpacked" and select the "ThoughtJot Extension" folder provided.
This will have installed the chrome extension so that it can be used with the flask application. 

## Using the Extension 
The extension is primarily used by right clicking on selected text and then pressing the "Jot!" context menu. To make this feature functional, an account is needed on the web app. While the web app is running, register a user and copy their key from the "Get Key" tab. There is helpful information about the key on the `/help` route of the web app. Navigate to the extension's "options" through right clicking on its icon in the corner of chrome, or through the chrome extensions menu. Clicking options will open a form that allows a key to be inputted. Paste the key from the web app into the form and hit "Confirm". Now, using the "Jot!" context menu will send the data selected to the account corresponding to the key.

To view the Jots that were sent from the chrome extension, log onto the account with the key that corresponds with the one in the extension. Upon logging in, a table with all the jots will be displayed.  

### Resetting Keys
Keys vital to the communication between the web app and the chrome extension. These keys allow for writing of Jots to a user's account, so it is important that these are kept private. If one is compromised, there exists the option in the web application `/key` route to reset the key and get a brand new one to use. The key will only be updated on the web server, so it is still necessary to go through the extension's options menu to update it to the new one. 

## Youtube Video
`https://youtu.be/536V2tuJk2s`
