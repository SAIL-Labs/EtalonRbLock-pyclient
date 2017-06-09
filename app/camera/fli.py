

import os

import FLI
from astropy.io import fits

from .camera import AbstractCamera


class Camera(AbstractCamera):
    """
    
    """

    _cam = None

    def __init__(self,
                 name='FLI M8300',
                 set_point=10,
                 *args, **kwargs):
        """
        
        :param name: 
        :type name: 
        :param set_point: 
        :type set_point: 
        :param args: 
        :type args: 
        :param kwargs: 
        :type kwargs: 
        """
        kwargs['readout_time'] = 2.4
        kwargs['file_extension'] = 'fits'
        super().__init__(name, *args, **kwargs)


        self.connect()
        # Set cooling (if set_point=None this will turn off cooling)
        if self.is_connected:
            self.CCD_set_point = set_point
            self.logger.info('\t\t\t {} initialised'.format(self))

    def connect(self, setpoint=None):
        """
        
        :param setpoint: 
        :type setpoint: 
        :return: 
        :rtype: 
        """
        cams = FLI.camera.USBCamera.find_devices()

        try:
            self._cam = cams[0]
        except IndexError as err:
            self.logger.error('Could not connect to {}!'.format(self.name))
            return
            # raise err

        self.logger.debug("{} connected".format(self.name))
        self._connected = True

        self._info = self._cam.get_info()
        self._serial_number = self._info['serial_number']

    @AbstractCamera.uid.getter
    def uid(self):
        """"
        """
        # Unlike Canon DSLRs 1st 6 characters of serial number is *not* a unique identifier.
        # Need to use the whole thing.
        return str(self._serial_number)

    @property
    def CCD_temp(self):
        return self._cam.read_CCD_temperature()

    @property
    def base_temp(self):
        return self._cam.read_base_temperature()

    @property
    def CCD_set_point(self):
        return self.__CCD_set_point

    @property
    def CCD_exposure(self):
        return self.__CCD_exposure

    @CCD_exposure.setter
    def CCD_exposure(self, exposure_length):
        """
        
        :param exposure_length: 
        :type exposure_length: 
        :return: 
        :rtype: 
        """
        self._cam.set_exposure(exposure_length)
        self.__CCD_exposure = exposure_length

    @CCD_set_point.setter
    def CCD_set_point(self, set_point):
        #self.logger.debug("Setting {} cooling set point to {}".format(self.name, set_point))
        self._cam.set_temperature(set_point)
        self.__CCD_set_point = set_point

    def save_image_to_fits(self, imagetime, imdata, filename, exposuretime, temp, pressure, hum):
        header = fits.Header()
        header.set('INSTRUME', self.uid)
        header.set('DATE-OBS', imagetime.fits)
        header.set('JD_T', imagetime.jd)
        header.set('MJD_T', imagetime.mjd)
        header.set('Unix_T', imagetime.unix)
        header.set('EXPTIME', exposuretime)
        header.set('CCD-TEMP', self.CCD_temp)
        header.set('BASETEMP', self.base_temp)
        header.set('SET-TEMP', self.CCD_set_point)
        header.set('EXT-TEMP', temp)
        header.set('EXT-PRES', pressure)
        header.set('SET-HUMD', hum)

        # Write to FITS file. Includes basic headers directly related to the camera only.
        hdu = fits.PrimaryHDU(imdata, header=header)
        # Create the images directory if it doesn't already exist
        if os.path.dirname(filename):
            os.makedirs(os.path.dirname(filename), mode=0o766, exist_ok=True)
        hdu.writeto(filename)
        self.logger.debug('Image written to {}'.format(filename))
