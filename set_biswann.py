from ebk_status import is_open
import datetime
import json
import logging
import paho.mqtt.client as mqtt
import time
import telnetlib

logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)s '
                        '%(levelname)s %(message)s')
log = logging.getLogger(__name__)


mqtt_client = mqtt.Client()
mqtt_client.enable_logger(logger=log)
mqtt_client.connect('putin')
mqtt_client.publish('space/status/biswann', '2200')

