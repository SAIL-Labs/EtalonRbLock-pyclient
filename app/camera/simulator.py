import os
import subprocess

from threading import Event
from threading import Timer

from astropy import units as u

from ..utils import current_time
#from ..utils import error

from .camera import AbstractCamera


class Camera(AbstractCamera):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger.debug("Initializing simulator camera")

        # Simulator
        self._serial_number = '999999'

    def connect(self):
        """ Connect to camera simulator

        The simulator merely markes the `connected` property.
        """
        self._connected = True
        self.logger.debug('Connected')

    def take_observation(self, observation, headers=None, **kwargs):
        camera_event = Event()

        if headers is None:
            headers = {}

        start_time = headers.get('start_time', current_time(flatten=True))

        filename = "solved.{}".format(self.file_extension)

        file_path = "{}/pocs/tests/data/{}".format(os.getenv('POCS'), filename)

        image_id = '{}_{}_{}'.format(
            self.config['name'],
            self.uid,
            start_time
        )
        self.logger.debug("image_id: {}".format(image_id))

        sequence_id = '{}_{}_{}'.format(
            self.config['name'],
            self.uid,
            observation.seq_time
        )

        # Camera metadata
        metadata = {
            'camera_name': self.name,
            'camera_uid': self.uid,
            'field_name': observation.field.field_name,
            'file_path': file_path,
            'filter': self.filter_type,
            'image_id': image_id,
            'is_primary': self.is_primary,
            'sequence_id': sequence_id,
            'start_time': start_time,
        }
        metadata.update(headers)
        exp_time = kwargs.get('exp_time', observation.exp_time.value)

        if exp_time > 5:
            self.logger.debug("Trimming camera simulator exposure to 5 s")
            exp_time = 5

        self.take_exposure(seconds=exp_time, filename=file_path)

        # Process the image after a set amount of time
        wait_time = exp_time + self.readout_time
        t = Timer(wait_time, self.process_exposure, (metadata, camera_event,))
        t.name = '{}Thread'.format(self.name)
        t.start()

        return camera_event

    def take_exposure(self, seconds=1.0 * u.second, filename=None):
        """ Take an exposure for given number of seconds """

        assert filename is not None, self.logger.warning("Must pass filename for take_exposure")

        if isinstance(seconds, u.Quantity):
            seconds = seconds.value

        self.logger.debug('Taking {} second exposure on {}'.format(seconds, self.name))

        # Simulator just sleeps
        run_cmd = ["sleep", str(seconds)]

        # Send command to camera
        try:
            proc = subprocess.Popen(run_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        except error.InvalidCommand as e:
            self.logger.warning(e)

        return proc

    def process_exposure(self, info, signal_event):
        """Processes the exposure

        Args:
            info (dict): Header metadata saved for the image
            signal_event (threading.Event): An event that is set signifying that the
                camera is done with this exposure
        """
        image_id = info['image_id']
        file_path = info['file_path']
        self.logger.debug("Processing {} {}".format(image_id, file_path))

        self.db.insert_current('observations', info, include_collection=False)

        self.logger.debug("Adding image metadata to db: {}".format(image_id))
        self.db.observations.insert_one({
            'data': info,
            'date': current_time(datetime=True),
            'type': 'observations',
            'image_id': image_id,
        })

        # Mark the event as done
        signal_event.set()
