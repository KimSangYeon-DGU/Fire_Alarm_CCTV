# Server
<h3><b>A Server that mediates Raspberry Pi 3 and Android apps</b></h3>

# Features
- Image streaming between CCTV and client.
- Fire detection and notification.
- Access to Real-time database in Firebase.
- Recording in a video format per day.

# Installation
- Install TensorFlow (In my case, I installed version 1.9.0)

    <code>
        ex) pip install tensorflow==1.9.0
        - pip install tensorflow==[version]
    </code>
    
- Install OpenCV
    - conda install -c menpo opencv
    
- Install FCM
    - pip install pyfcm
    
- Install Firebase
    - pip install requests
    - pip install python-firebase

# Libraries
    - FCM(Firebase Cloud Messaging)
        - pip install pyfcm
    - Firebase(Real-time database)
        - pip install requests
        - pip install python-firebase

# Environment
- Windows10
- Anaconda3 
- Python3 (3.6, but firebase library doesn't work in 3.7)
