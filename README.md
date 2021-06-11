# Code-Snip
This project is born for the "web technologies" exam at the University of Naples Parthenope.

HOW TO RUN:
To run the web app locally, follow these instructions:

1. Pull the project and link correctly the Python interpreter for the virtual environment.
   - To do so in PyCharm, go to Settings -> Project: Code Snip -> Python Interpreter and select your interpreter of choice, then add a configuration and select it.
   - Alternatively, you can install the few required modules (found in requirements.txt) manually and run it as you please.
2. Install docker, open the terminal and follow these instructions to set it up correctly:
   1) docker pull mongo
   2) docker volume create --name=mongodata
   3) docker run --name mongodb -v mongodata:/data/db -d -p 27017:27017 mongo
3. Run app.py (which is found in the root folder of the project).
4. Open your browser to localhost.
5. Enjoy Code Snippet!
