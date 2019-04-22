import datetime
import json
import logging
import paho.mqtt.client as mqtt
import time


logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)s '
                        '%(levelname)s %(message)s')
log = logging.getLogger(__name__)


mqtt_client = mqtt.Client()
mqtt_client.enable_logger(logger=log)
mqtt_client.connect('putin')
mqtt_client.subscribe('/esp32ebttest/wie')
mqtt_client.subscribe('/esp32ebttest/bis')
mqtt_client.subscribe('space/status/open')

CURRENT_HOWLONG = None


def set_output(closetime=None):
    with open('/home/spaceapi/spaceapi/htdocs/openuntil.json', 'w') as outfile:
        CURRENT_HOWLONG = closetime
        out_data = dict(closetime=closetime)
        outfile.write(json.dumps(out_data))


def mqtt_received(client, data, msg):
    opentopic = 'space/status/open'
    if msg.topic == opentopic and msg.payload.decode('utf8') != 'true':
        log.info('Space closed, reset wielange time info.')
        set_output()
        return
    log.info('Received msg from wiebis: {}, containing {}'.format(
                msg.topic, msg.payload))
    value = int(msg.payload)
    hours = value // 100
    minutes = value - (hours * 100)
    if msg.topic.endswith('bis'):
        # uhrzeit
        set_output(datetime.time(hours, minutes).strftime('%H:%M'))
    elif msg.topic.endswith('wie'):
        # stunden:minuten ab jetzt
        fromnow = datetime.timedelta(hours=hours, minutes=minutes)
        closedt = datetime.datetime.now() + fromnow
        set_output(closedt.strftime('%H:%M'))
    



mqtt_client.on_message = mqtt_received
mqtt_client.loop_start()


while True:
    curdt = datetime.datetime.now().strftime('%H:%M')
    if curdt == CURRENT_HOWLONG:
        # time reached, resetting output
        set_output()

    time.sleep(1)

