import PySpin
import cv2
import numpy as np

def main():
    # Get system
    system = PySpin.System.GetInstance()

    # Get camera list
    cam_list = system.GetCameras()

    if cam_list.GetSize() == 0:
        print("No cameras found")
        system.ReleaseInstance()
        return

    # Get the first camera in the list
    camera = cam_list.GetByIndex(0)

    try:
        # Initialize the camera
        camera.Init()

        # Configure the camera for acquisition
        camera.BeginAcquisition()

        # Setup video writer
        output_filename = 'output_video.avi'  # Specify your output file name here
        codec = cv2.VideoWriter_fourcc(*'XVID')  # Specify codec
        framerate = 20.0  # Specify framerate
        # We'll set the frame size after getting the first frame

        first_frame = True
        video_writer = None

        # Loop over frames you want to acquire (example: 100 frames)
        for _ in range(100):
            image_ptr = camera.GetNextImage()
            if image_ptr.IsIncomplete():
                print('Image incomplete with image status %d ...' % image_ptr.GetImageStatus())
                continue

            # Retrieve the image data
            image_data = image_ptr.GetData()

            # Get image dimensions
            width = image_ptr.GetWidth()
            height = image_ptr.GetHeight()

            if first_frame:
                # Initialize the video writer once we know the frame size
                video_writer = cv2.VideoWriter(output_filename, codec, framerate, (width, height))
                first_frame = False

            # Convert the image data to a NumPy array
            image_array = np.array(image_data).reshape((height, width, 3))

            # Convert from RGB to BGR format for OpenCV
            image_opencv = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)

            # Write frame to video
            video_writer.write(image_opencv)

            # Release image
            image_ptr.Release()

        # Stop acquisition
        camera.EndAcquisition()

        # Release the camera
        camera.DeInit()

        # Check if video writer was created and release
        if video_writer is not None:
            video_writer.release()
            print(f"Video saved as {output_filename}")

    except PySpin.SpinnakerException as e:
        print("Error: %s" % e)

    finally:
        # Release the camera and the system
        del camera
        cam_list.Clear()
        system.ReleaseInstance()

if __name__ == "__main__":
    main()
