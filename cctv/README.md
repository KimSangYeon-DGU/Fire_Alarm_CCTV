# CCTV
<h3><b>A CCTV that watch specific area and send frames to server in real time</b></h3>

# DEMO
<p align="center">
    <img src="/images/cctv_demo.gif", width="480">
</p>

# Features
- Sending the frames to server in real time

# Prerequisites
- Python 3.5+
- OpenCV 3.4+

# Installation
- Update the Raspberry Pi 3

      sudo apt-get update
      sudo apt-get dist-upgrade

- Install OpenCV
        
      sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
      sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
      sudo apt-get install libxvidcore-dev libx264-dev
      sudo apt-get install qt4-dev-tools
      
      pip3 install opencv-python

# Run
    python camera.py
