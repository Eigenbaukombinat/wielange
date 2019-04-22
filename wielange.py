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
mqtt_client.subscribe('/space/status/open')


def mqtt_received(client, data, msg):
	opentopic = '/space/status/open'
	if msg.topic == opentopic and msg.payload.decode('utf8') != 'true':
		log.info('Space closed, reset wielange time info.')
		closetime = None
	elif topic.startswith('/esp32ebttest'):
		log.info('Received msg from wiebis: {}, containing {}'.format(
					msg.topic, msg.payload))
		value = int(msg.payload)
		hours = value // 100
		minutes = value - (hours * 100)
		if msg.topic.endswith('bis'):
			# uhrzeit
			closetime = datetime.time(hours, minutes).strftime('%H:%M')
		elif msg.topic.endswith('wie'):
			# stunden:minuten ab jetzt
			fromnow = datetime.timedelta(hours=hours, minutes=minutes)
			closedt = datetime.datetime.now() + fromnow
			closetime = closedt.strftime('%H:%M')

	with open('openuntil.json', 'w') as outfile:
		out_data = dict(closetime=closetime)
		outfile.write(json.dumps(out_data))



mqtt_client.on_message = mqtt_received
mqtt_client.loop_start()


while True:
	time.sleep(1)

