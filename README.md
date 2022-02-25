# Moco_RCCar_Server
Repo for Motion Control RCCar Server

install opencv: pip install opencv-contrib-python

Note: contrib modules contains Aruco library, s. https://docs.opencv.org/3.4/d3/d81/tutorial_contrib_root.html

TODO!!!:

.

.

.

Change:
    
    corner.trj path in Server/Configuration.py/Detection
    parking.trj path in Server/Trajectory.py/RcAdaptiveTrajectory/init and replace the file with the "create new path" 
    continue.trj path in Server/Trajectory.py/RcAdaptiveTrajectory/init and replace the file with the "create new path"

You can generate ArUco in https://chev.me/arucogen/.

The app is using "Original arUco" Dictionary.

        tagID_topLeft = 65
        tagID_topRight = 85
        tagID_bottomRight = 0
        tagID_bottomLeft = 63
        tagID_car = 21
The corner ids can be changed in State_CornerDetection.py/on_enter and car id in State_ControlCar.py/run.
