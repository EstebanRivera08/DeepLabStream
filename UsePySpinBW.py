import PySpin
import cv2
import numpy as np



def main():
    # Initialize PySpin system
    system = PySpin.System.GetInstance()

    # Get camera list
    cam_list = system.GetCameras()

    if len(cam_list) == 0:
        print("No cameras found.")
        return

    try:
        # Get the first camera
        camera = cam_list.GetByIndex(0)

        # Initialize camera
        camera.Init()

        
        # Capture an image
        print("Acquiring images...")
        camera.BeginAcquisition()

        
        # Grab a single image
        image = camera.GetNextImage()
        
        #image = capture_color_image(image)
        
        # Convert image to numpy array
        image_data = image.GetNDArray()
        
        print(np.shape(image_data))
        # Display the image
        cv2.imshow("FLIR Camera Image", image_data)
        cv2.waitKey(0)

        # Release image
        image.Release()
        
        # Stom acquisition
        camera.EndAcquisition()
        
        # Release the camera
        camera.DeInit()

    except PySpin.SpinnakerException as e:
        print("Error: %s" % e)
        return

    # Release the camera and the system
    
    del camera
    cam_list.Clear()
    system.ReleaseInstance()



if __name__ == "__main__":
    main()


