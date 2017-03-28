#import shutil
from .. import erlBase

class AbstractCamera(erlBase):
    """ Base class for all cameras """

    def __init__(self,
                 name='Generic Camera',
                 model='simulator',
                 port=None,
                 *args, readout_time=5.0, file_extension='fits', **kwargs):

        super().__init__(*args, **kwargs)

        try:
            self._image_dir = self.config.image_directory
        except KeyError:
            self.logger.error("No images directory. Set image_dir in config")

        self.model = model
        self.port = port
        self.name = name

        self._connected = False
        self._serial_number = 'XXXXXX'
        self._readout_time = readout_time
        self._file_extension = file_extension

        self.properties = None
        self._current_observation = None


        self.logger.debug('Camera created: {}'.format(self))

##################################################################################################
# Properties
##################################################################################################

    @property
    def uid(self):
        """ A six-digit serial number for the camera """
        return self._serial_number[0:6]

    @property
    def is_connected(self):
        """ Is the camera available vai gphoto2 """
        return self._connected

    @property
    def readout_time(self):
        """ Readout time for the camera in seconds """
        return self._readout_time

    @property
    def file_extension(self):
        """ File extension for images saved by camera """
        return self._file_extension

    @property
    def CCD_temp(self):
        """
        Get current temperature of the camera's image sensor.

        Note: this only needs to be implemented for cameras which can provided this information,
        e.g. those with cooled image sensors.
        """
        raise NotImplementedError

    @property
    def CCD_set_point(self):
        """
        Get current value of the CCD set point, the target temperature for the camera's
        image sensor cooling control.

        Note: this only needs to be implemented for cameras which have cooled image sensors,
        not for those that don't (e.g. DSLRs).
        """
        raise NotImplementedError

    @CCD_set_point.setter
    def CCD_set_point(self, set_point):
        """
        Set value of the CCD set point, the target temperature for the camera's image sensor
        cooling control.

        Note: this only needs to be implemented for cameras which have cooled image sensors,
        not for those that don't (e.g. DSLRs).
        """
        raise NotImplementedError

    @property
    def CCD_cooling_enabled(self):
        """
        Get current status of the camera's image sensor cooling system (enabled/disabled).

        Note: this only needs to be implemented for cameras which have cooled image sensors,
        not for those that don't (e.g. DSLRs).
        """
        raise NotImplementedError

    @property
    def CCD_cooling_power(self):
        """
        Get current power level of the camera's image sensor cooling system (typically as
        a percentage of the maximum).

        Note: this only needs to be implemented for cameras which have cooled image sensors,
        not for those that don't (e.g. DSLRs).
        """
        raise NotImplementedError

##################################################################################################
# Methods
##################################################################################################

    def take_observation(self, *args, **kwargs):
        raise NotImplementedError

    def take_exposure(self, *args, **kwargs):
        raise NotImplementedError

    def process_exposure(self, *args, **kwargs):
        raise NotImplementedError

    def __str__(self):
        try:
            return "{} ({}) on {} with {} focuser".format(self.name, self.uid, self.port, self.focuser.name)
        except AttributeError:
            return "{} ({}) on {}".format(self.name, self.uid, self.port)

    def save_image_to_fits(self, imagetime, imdata, filename, exposuretime):
        raise NotImplementedError
