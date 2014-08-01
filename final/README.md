CS 8803: Final Project - Hexbug Tracker - Magahet Mendiola
=======================================


# Overview

This project includes code to track and predict the path of the hexbug by using the provided centroid data files. It performs this task by modeling the state of the hexbug with a Kalman Filter, a constant acceleration model, and a basic physics engine. Details for how to execute the program and details regarding implementation can be found in this guide and within the code documentation.


# Quickstart

To get the final result for the purposes of grading, run the following command:

    ./predict.py -f 63 -s 1200 -m 49.97 -p 83.32 -a 0.17 -t testing_video-centroid_data


This will output the final 63 predicted points on the hexbug's path:

    [(609, 326), (604, 333), (598, 341), (593, 349), (587, 357), (580, 364), (574, 372), (568, 379), (561, 387), (554, 394), (547, 402), (540, 409), (532, 417), (525, 418), (517, 417), (509, 415), (501, 414), (492, 413), (484, 412), (475, 411), (466, 409), (457, 408), (448, 407), (438, 406), (428, 405), (419, 403), (408, 402), (398, 401), (388, 400), (377, 399), (366, 398), (355, 397), (344, 395), (333, 394), (321, 393), (309, 392), (297, 391), (285, 390), (273, 389), (260, 388), (248, 387), (235, 386), (222, 384), (208, 383), (195, 382), (181, 381), (167, 380), (168, 379), (171, 378), (173, 377), (176, 376), (178, 375), (181, 374), (183, 373), (186, 372), (189, 371), (191, 370), (194, 369), (197, 368), (199, 367), (202, 366), (205, 365), (208, 365)]


# Project Componants

The project consists of the following modules, classes, and functions:

## predict.py

predict.py contains the tracking and prediction function.

    usage: predict.py [-h] [--forecast forecast] [--turtle] [--start START]
                      [--end END] [--length LENGTH]
                      [--measurement_error MEASUREMENT_ERROR]
                      [--process_error PROCESS_ERROR]
                      [--absorption_factor ABSORPTION_FACTOR]
                      centroid_file

    Predict the hexbug path.

    positional arguments:
      centroid_file         file containing hexbug centroid data

    optional arguments:
      -h, --help            show this help message and exit
      --forecast forecast, -f forecast
                            number of frames to predict
      --turtle, -t          enable turtle visualization
      --start START, -s START
                            starting frame
      --end END, -e END     ending frame
      --length LENGTH, -l LENGTH
                            number of frames
      --measurement_error MEASUREMENT_ERROR, -m MEASUREMENT_ERROR
                            measurement error
      --process_error PROCESS_ERROR, -p PROCESS_ERROR
                            process error
      --absorption_factor ABSORPTION_FACTOR, -a ABSORPTION_FACTOR
                            absorption factor

Example:

    ./predict.py -f 63 -s 100 -l 200 -m 49.97 -p 83.32 -a 0.17 -t testing_video-centroid_data

This will predict 63 frames of the path after tracking the hexbug position from frame 100 for 200 frames. Measurement and process noise parameters are used by the Kalman filter to adjust how much confidence is placed on measurement and prediction updates. The absorption factor is used by the physics engine to adjust how the model reacts when it encounters a wall.


## kalman.py

kalman.py includes classes to perform state modeling in 2D.

kalman.KalmanFilterModel2DCam provides a Kalman filter with a constant acceleration model. It maintains a 1x6 state matrix of position, velocity, and acceleration in x and y. It includes separate methods for prediction and measurement updates. It also provides a method to manually adjust the state matrix and reset the error covariance matrix. This is useful for quickly adapting to abrupt state changes such as those caused when running into a wall.


## bb.py

bb.py includes a class to model the environmental constraints imposed by the box containing the hexbug.

bb.BoundingBox provides a model for the walls surrounding the hexbug. It allows for checking if predicted points fall outside the box, and methods to calculate bouncing off or limiting points to within the walls.
