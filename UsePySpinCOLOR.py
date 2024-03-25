import PySpin
import cv2
import numpy as np

def main():
    # Get system
    system = PySpin.System.GetInstance()

    # Get camera list
    cam_list = system.GetCameras()

    # Get the first camera in the list
    camera = cam_list.GetByIndex(0)

    try:
        # Initialize the camera
        camera.Init()

        # Retrieve GenICam nodemap
        nodemap = camera.GetNodeMap()

        # Get the enumeration node
        node_pixel_format = PySpin.CEnumerationPtr(nodemap.GetNode('PixelFormat'))

        # Check if the node is available
        if PySpin.IsAvailable(node_pixel_format) and PySpin.IsReadable(node_pixel_format):
            # Get a list of entries
            entries = node_pixel_format.GetEntries()

            # Print the symbolic name of each entry
            for entry in entries:
                enum_entry = PySpin.CEnumEntryPtr(entry)
                if PySpin.IsAvailable(enum_entry) and PySpin.IsReadable(enum_entry):
                    print(f"- {enum_entry.GetSymbolic()}")
        
        # List of color formats to try
        color_formats = ['RGB8']

        for format in color_formats:
            node_pixel_format_color = node_pixel_format.GetEntryByName(format)
            if PySpin.IsAvailable(node_pixel_format_color) and PySpin.IsReadable(node_pixel_format_color):
                pixel_format_color = node_pixel_format_color.GetValue()
                node_pixel_format.SetIntValue(pixel_format_color)
                print(f'Successfully set PixelFormat to {format}')
                break
        else:
            print('Unable to set any color PixelFormat. Aborting...')
        
            system.ReleaseInstance()
            return


            # Start acquisition
        camera.BeginAcquisition()

        # Retrieve image from camera
        image_ptr = camera.GetNextImage()

        # Retrieve the image data
        image_data = image_ptr.GetData()

        # Get image dimensions
        width = image_ptr.GetWidth()
        height = image_ptr.GetHeight()

        # Convert the image data to a NumPy array
        image_array = np.array(image_data).reshape((height, width, 3))

        # Convert from RGB to BGR format for OpenCV
        image_opencv = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)

        # Display the image with OpenCV
        cv2.imshow('Image', image_opencv)
        cv2.waitKey(0)

        # Release image
        image_ptr.Release()

        # Stop acquisition
        camera.EndAcquisition()

        # Release the camera
        camera.DeInit()

    except PySpin.SpinnakerException as e:
        print("Error: %s" % e)
        
        system.ReleaseInstance()
        return

    # Release the camera and the system
    del camera
    cam_list.Clear()
    system.ReleaseInstance()

if __name__ == "__main__":
    main()