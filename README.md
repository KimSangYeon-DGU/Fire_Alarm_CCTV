# OSSP_Fire_Alarm_CCTV
This is the repository for 2018 OSS Grand Developers Challenge

# What functionality has the CCTV?
- It detects the fire situation and inform users of that. It shows the fire picture users so the user exactly can check it. It plan to use an artificial intelligence and an image processing methods.

# Overall Architecture
<p align="center">
    <img src="images/architecture.PNG", width="640">
</p>

# Timeline
<p align="center">
    <img src="images/gantt-chart.png", width="1024", height="512">
</p>

# TODO List        
<b>4. Train custom model</b>

<b>5. Test model</b>

<b>6. If needed, Increase a performance of the model
    
<b>7. Make server application (currently working)
  
<b>8. Make client application
    
<b>9. System Test</b>

# Done
<b>1. Gather the information</b>

    - Check which Raspberry pi model and camera fits the project
        - I decided to buy Raspberry pi 3 B+, as It is improved by 17% than previous model, and pi camera because I heard that It uses GPU when processing an image.
    - How to transplant deep learning model on Raspberry pi 3
        - Check the link
    - Which deep learning model is used
    - Fire images
        - Use opened datasets, I assume that the number of images is 2,000 first.
    - What development environment you use to train the deep learning model
        - I will use AWS EC2 P3 Instance on Windows 10
        
<b>2. Test Demo model on Raspberry Pi 3 B+</b>

    - Succeeded run demo model on Raspberry Pi 3 B+, and the fps is about lower than 1.6
    
<b>3. Make train dataset</b>

    - Make train dataset(total 1815, will be splited into train and test)

<b>[DEMO]</b>

    - Make demo server and client(success connecting python server and android client using TCP socket.)

# Useful Links
- The mothod to transplant deep learning model on Raspberry pi 3
    - https://github.com/EdjeElectronics/TensorFlow-Object-Detection-on-the-Raspberry-Pi
    
# Useful info
The TOD(TensorFlow Object Detection) on the Raspberry Pi run environments are Tensorflow 1.5, cudNN 7.0 and cuda 8.0(Those are the best setting without error)

# Performance objectives
The information should be gathered to decide performance of the CCTV, so I don't state it yet.

# God Bless You
