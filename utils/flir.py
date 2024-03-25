import PySpin
import cv2
import numpy as np

class FLIRManager:
    """
    FLIR cameras manager class
    """

    def __init__(self):
        """
        Initialize the FLIR camera environment.
        """
        self._manager_name = "FLIR"
        self._system = PySpin.System.GetInstance()
        self._factory = self._system.GetCameras()
        self._enabled_devices = {}
        self._resolution = None

    @property
    def _connected_devices(self) -> dict:
        """
        Create a dict with all connected devices
        """
        return {
            cam.GetUniqueID(): cam
            for cam in self._factory
        }

    def get_connected_devices(self) -> list:
        """
        Getter for stored connected devices
        """
        return list(self._connected_devices.keys())

    def enable_stream(self, resolution, *args):
        """
        Enable stream with given parameters
        Pretty meaningless for FLIR manager, just sets the desired resolution
        """
        self._resolution = resolution

    def enable_device(self, device_serial: str, *args):
        """
        Camera starter, adapted to closely align with the Pylon example structure
        and enhanced for better error handling and consistency.
        """
        try:
            if device_serial not in self.get_connected_devices():
                print(f"Error: Serial {device_serial} not found among connected devices.")
                return
            
            camera = self._connected_devices[device_serial]
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
                print('Available PixelFormat options:')
                for entry in entries:
                    enum_entry = PySpin.CEnumEntryPtr(entry)
                    if PySpin.IsAvailable(enum_entry) and PySpin.IsReadable(enum_entry):
                        print(f"- {enum_entry.GetSymbolic()}")

            # SELECTED FORMAT
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
                return


            camera.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
            camera.BeginAcquisition()
            self._enabled_devices[device_serial] = camera
        except PySpin.SpinnakerException as e:
            print(f"Error enabling FLIR camera {device_serial}: {e}")

    def enable_all_devices(self):
        """
        Enable all detected devices
        """
        for device in self._connected_devices:
            self.enable_device(device)

    def get_enabled_devices(self) -> dict:
        """
        Getter for enabled devices dictionary
        """
        return self._enabled_devices

    def get_frames(self) -> tuple:
        """
        Collect frames for cameras and outputs it in 'color' dictionary
        """
        color_frames = {}
        for device_serial, camera in self._enabled_devices.items():
            try:
                image_result = camera.GetNextImage(5000)
                if image_result.IsIncomplete():
                    print(f"Image incomplete: {image_result.GetImageStatus()}")
                    continue
                else:
                    # Ensure correct handling of color data and resizing
                    # Retrieve the image data
                    image_data = image_result.GetData()

                    # Get image dimensions
                    width = image_result.GetWidth()
                    height = image_result.GetHeight()

                    # Convert the image data to a NumPy array
                    image_array = np.array(image_data).reshape((height, width, 3))

                    # Convert from RGB to BGR format for OpenCV
                    image_data = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)

                    if self._resolution:
                        image_data = cv2.resize(image_data, self._resolution)

                    color_frames[device_serial] = image_data

            except PySpin.SpinnakerException as e:
                print(f"Error retrieving frame from FLIR camera {device_serial}: {e}")
            finally:
                image_result.Release()

        return color_frames, {}, {}  # depth_maps and infra_frames not used, returning empty

    def stop(self):
        """
        Stops cameras and cleans up
        """
        for camera in self._enabled_devices.values():
            camera.EndAcquisition()
            camera.DeInit()
        self._enabled_devices = {}

        # Cleanup: Clear camera list before releasing system instance
        #self._factory.Clear()
        #self._system.ReleaseInstance()

    def get_name(self) -> str:
        return self._manager_name
