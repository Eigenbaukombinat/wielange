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
mqtt_client.subscribe('space/status/wielange')
mqtt_client.subscribe('space/status/biswann')
mqtt_client.subscribe('space/status/open')


def telnet(txt):
    try:
        telnet = telnetlib.Telnet('192.168.21.148')
    except:
        logging.error('Cannot connect to display, make sure it is on the network with IP 192.168.21.148')
        return
    telnet.write('\n\n'.encode('latin1'))
    telnet.write(chr(0x0D).encode('latin1')) #0x0D clear; 0x0F All Display; 0x0B scroll; 
    telnet.write(chr(0x10).encode('latin1'))  ##Displayposition   0x10  
    telnet.write(chr(0).encode('latin1'))    ##Position
    telnet.write(txt.encode('latin1'))


def set_output(client, closetime=None):
    if closetime is not None:
        display_text(client, 'offen bis: %s - Willkommen im Eigenbaukombinat' % closetime)
        client.publish('space/status/closetime', closetime)
    with open('/home/spaceapi/spaceapi/htdocs/openuntil.json', 'w') as outfile:
        out_data = dict(closetime=closetime)
        outfile.write(json.dumps(out_data))


def display_text(client, text):
    telnet(text)
    client.publish('display/ledlaufschrift/text', text)

def mqtt_received(client, data, msg):
    opentopic = 'space/status/open'
    if msg.topic == opentopic:
        if msg.payload.decode('utf8') != 'true':
            log.info('Space closed, reset wielange time info.')
            set_output(client)
        else:
            log.info('Space opened, reset wielange time info.')
            set_output(client)
            display_text(client, b'space offen, bitte zeit setzen')
        return
    log.info('Received msg from wiebis: {}, containing {}'.format(
                msg.topic, msg.payload))
    value = int(msg.payload)
    hours = value // 100
    minutes = value - (hours * 100)
    if msg.topic.endswith('biswann'):
        # uhrzeit
        set_output(client, datetime.time(hours, minutes).strftime('%H:%M'))
    elif msg.topic.endswith('wielange'):
        # stunden:minuten ab jetzt
        fromnow = datetime.timedelta(hours=hours, minutes=minutes)
        closedt = datetime.datetime.now() + fromnow
        set_output(client, closedt.strftime('%H:%M'))


mqtt_client.on_message = mqtt_received
mqtt_client.loop_start()


while True:
    curdt = datetime.datetime.now().strftime('%H:%M')
    with open('/home/spaceapi/spaceapi/htdocs/openuntil.json', 'r') as howlong:
        howlongdata = json.loads(howlong.read())
    if curdt == howlongdata['closetime']:
        # time reached, resetting output
        display_text(mqtt_client, 'schliesszeit erreicht, bitte neu setzen oder space schliessen')
        set_output(mqtt_client)

    time.sleep(5)

