# Server
<h3><b>A Server that mediates Raspberry Pi 3 and Android apps</b></h3>

# DEMO
<p align="center">
    <img src="/images/server_demo.gif", width="480">
</p>

# Features
- Image streaming between CCTV and client.
- Fire detection and notification.
- Access to Real-time database in Firebase.
- Record frames in a video format per day.

# Prerequisites
- Windows10
- Anaconda3 
- Python3.6 (but firebase library doesn't work in 3.7)
- CUDA 9.0
- cuDNN 7.2.1

# Installation
- Install TensorFlow (In my case, I installed version 1.9.0)

      Ex) pip install tensorflow-gpu==1.9.0
      pip install tensorflow-gpu==[version]

- Install OpenCV
        
      conda install -c menpo opencv
    
- Install FCM
        
      pip install pyfcm
    
- Install Firebase
        
      pip install requests       
      pip install python-firebase

# Run
    python Object_detection.py
