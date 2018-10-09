# Server
<h3><b>A Server that mediates Raspberry Pi 3 and Android apps</b></h3>

# Features
- Image streaming between CCTV and client.
- Fire detection and notification.
- Access to Real-time database in Firebase.
- Recording in a video format per day.

# Environment
- Windows10
- Anaconda3 
- Python3 (3.6, but firebase library doesn't work in 3.7)

# Installation
- Install TensorFlow (In my case, I installed version 1.9.0)

        Ex) pip install tensorflow==1.9.0
        pip install tensorflow==[version]

- Install OpenCV
        
        conda install -c menpo opencv
    
- Install FCM
        
        pip install pyfcm
    
- Install Firebase
        
        pip install requests       
        pip install python-firebase

# Run
    python Object_detection.py
