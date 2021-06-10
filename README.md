# Code-Snip
This project is born for the "web technologies" exam at the University of Naples Parthenope.

HOW TO RUN:
To run the web app locally, follow these instructions:

1. Pull the project and make sure to link correctly the Python interpreter for the virtual environment.
   - Alternatively, you can install the required modules (found in requirements.txt) manually.
2. Install docker and pull the most recent image of MongoDb (docker pull mongo).
3. Launch the container (docker run -it -v 27017:27017 --name mongodb -d mongo).   
4. Run app.py (which is found in the root folder of the project).
5. Open your browser in localhost.
6. Enjoy Code Snippet!
