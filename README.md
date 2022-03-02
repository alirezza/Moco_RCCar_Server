#Moco_RCCar_Server
Repo for Motion Control RCCar Server

## **_!!! please be careful and protect the car from falling down !!!_**
##Installation:
    install opencv: pip install opencv-contrib-python
    install Qt6: pip install PySide6
##Getting Started:

    1-conncet your cam to the computer
    2-find and replace the CamSelect in Configuration
    3-measure the table and replace the TrackWidth and TrackHeight in Confirguration
    4-make sure your firewall is disabled
    5-connect your wifi with the esp(name: "rccar", password: "123456789")
    6-run "Server"
    7-open the setting tab and click the "Reset Corners" button (do this everytime yaou change the cam position!)
    8-if the program finds the corners, it will display the current path
    9-click the "start car" button to start the car
    10-you can change the speed in setting tab with the speed slider
    11-click the "stop car" button the stop the car
    12-you can switch the path by clicking the "park", "continue" or "short round" in the main tab
    13-open the path tab for creating new paths
    14-click "create new path" button to see the path creating window
    15-draw the path by clicking on the creating window
    16-you can draw again by clicking the "clear path" button
    17-click "save path" to replace the old path
    18-click "lock in path" to switch to the control car state and press start
##Aruco:
You can generate ArUco in https://chev.me/arucogen/.

The app is currently using "Original arUco" Dictionary.

        tagID_topLeft = 65
        tagID_topRight = 85
        tagID_bottomRight = 0
        tagID_bottomLeft = 63
        tagID_car = 21
The corner ids can be changed in State_CornerDetection.py/on_enter and car id in State_ControlCar.py/run.
##Car setup:
[MotoDriver](/https://joy-it.net/de/products/SBC-Motodriver2)

Li-Ion battery
    
    7.4V, 1500mAh, 11.1Wh, discharge rate: 15C, max charge current: 5A
    max discharge current: 20A
[ESP8266 NodeMCU](https://components101.com/sites/default/files/component_datasheet/ESP8266-NodeMCU-Datasheet.pdf)

###Connection
![Circuit](./img/Circuit.png?raw=true "Circuit")
##GUI Guide:
###main:
![maintab](./img/maintab.png?raw=true "maintab")
####start car:
by clicking this button the car will first get a start power of 150 and continue with the vehicle_const_speed
####stop car:
by clicking this button the car will stop
####park:
by clicking this button the current path will change to parking path as soon as the car is in the change-path-area and the car will be stopped in the parking area.
####continue:
by clicking this button the current path will change to normal path as soon as the car is in the change-path-area and drive the path again and again.
####short round:
by clicking this button the current path will change to half path as soon as the car is in the change-path-area and drive the path again and again.
###path:
![pathtab](./img/pathtab.png?raw=true "pathtab")
####create new path:
by clicking this button the current state will change to `State_pathDetect` and a new windows will pop up, where you can draw a path by setting points on the window.
####lock in path:
by clicking this button the current state will change to the `State_ControlCar`.
####clear path:
by clicking this button the drawn path will be removed.
####save path:
by clicking this button you can save the drawn path as .trj file
####load path:
by clicking this button you can see the .trj file on the draw window
###setting:
![settingtab](./img/settingtab.png?raw=true "settingtab")
####reset state machine:
by clicking this button your state machine will begin again in the `State_CornerDetection`.
note: restart the GUI if it doesn't help, your thread may be stopped due some error.
####change direction:
by clicking this button you can change the direction of the path.
note: you have to change the path and set it again!
please stop the car and turn it to the right direction manually
####reset corners:
by clicking this button the corner.trj file will be removed and the current state will be changed to `State_CornerDetection`, and the program try to find the 
corner ids and save this again.
####speed slider:
by dragging this slider you can change the speed.
right for accelerate and left for decelerate.
##FAQ:
###how can I switch the path?
click the park, continue or short round button to change the path.

attention! the path does change when the car is in the change-path-area.
###how can I change the speed?
there are two ways:

1-change the initialized speed:

    1-open Configuration.py and change the vehicle_const_speed
2-change the current speed with the GUI

    1-click the setting tab
    2-drag the slider to the right to accelerate the car and left to decelerate the car
###how can I create my own path?
you can only replace the trajectory.

    1-click the path tab
    2-click the create new path button
    3-click draw your own path by setting point on the screen (click clear path to draw again)
    4-click save path button
    5-replace the old .trj file
    6-click lock in path
    
###how can I set new corners?
    1-click the setting tab
    2-click the reset corners button
###how can I change the camera?
    1-open Configuration.py and change the CamSelect
###why does the car not park?
this issue may be caused due the `isStopPoint()` function in Trajectory.

        1-open the GUI
        2-click the path tab
        3-click the "create new path" button
        4-draw 4 point for your parking-area
        5-the coordinates of the points will be printed in python terminal
        6-write down the coordinates
        7-replace the values in isStopPoint() with your new coordinates
    
###why is the path not changed?
this issue may be caused due the `isChangePoint()` function in Trajectory.

    1-open the GUI
    2-click the path tab
    3-click the "create new path" button
    4-draw 4 point for your change-path-area
    5-the coordinates of the points will be printed in python terminal
    6-write down the coordinates
    7-replace the values in isChangePoint() with your new coordinates
###why doesn't the car steer?
    1-restart the car and try it again
    2-restart the esp and try it again
    3-restart the gui and try it again
    4-flash the esp and try it again

