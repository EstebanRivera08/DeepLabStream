import PySpin
import cv2

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
            # Check if the device_serial is in the connected devices before proceeding
            if device_serial not in self.get_connected_devices():
                print(f"Error: Serial {device_serial} not found among connected devices.")
                return
            
            # Directly use the already identified connected device
            camera = self._connected_devices[device_serial]
            
            # Initialize and configure the camera for acquisition
            camera.Init()
            camera.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
            
            # Optionally, set additional camera parameters here before starting acquisition
            
            camera.BeginAcquisition()
            
            # Store the camera object, indexed by its serial number, for easy access
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
        ***depth and infrared are not used in FLIR***
        :return: tuple of three dictionaries: color, depth, infrared
        """
        color_frames = {}
        depth_maps = {}
        infra_frames = {}
        for device_serial, camera in self._enabled_devices.items():
            try:
                image_result = camera.GetNextImage(5000)  # Timeout in milliseconds
                if image_result.IsIncomplete():
                    print(f"Image incomplete: {image_result.GetImageStatus()}")
                else:
                    image_data = image_result.GetNDArray()
                    color_frames[device_serial] = cv2.resize(image_data, self._resolution)
            except PySpin.SpinnakerException as e:
                print(f"Error retrieving frame from FLIR camera {device_serial}: {e}")
        return color_frames, depth_maps, infra_frames

    def stop(self):
        """
        Stops cameras
        """
        for camera in self._enabled_devices.values():
            camera.EndAcquisition()
            camera.DeInit()
        self._enabled_devices = {}

    def get_name(self) -> str:
        return self._manager_name
