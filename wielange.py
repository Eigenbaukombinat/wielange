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


def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.subscribe('space/status/wielange')
        client.subscribe('space/status/biswann')
        client.subscribe('space/status/open')



mqtt_client = mqtt.Client()
mqtt_client.enable_logger(logger=log)
mqtt_client.on_connect = on_connect
mqtt_client.connect('putin')


def telnet(txt):
    try:
        telnet = telnetlib.Telnet('vfddisplay.lan')
    except:
        logging.error('Cannot connect to display, make sure it is on the network with vfddisplay.lan')
        return
    telnet.write('\n\n'.encode('latin1'))
    telnet.write(chr(0x0D).encode('latin1')) #0x0D clear; 0x0F All Display; 0x0B scroll; 
    telnet.write(chr(0x10).encode('latin1'))  ##Displayposition   0x10  
    telnet.write(chr(0).encode('latin1'))    ##Position
    telnet.write(txt.encode('latin1'))


def write_json(closetime):
    with open('/home/spaceapi/spaceapi/htdocs/openuntil.json', 'w') as outfile:
        out_data = dict(closetime=closetime)
        outfile.write(json.dumps(out_data))


def set_output(client, closetime):
    if not is_open():
        display_text(client, 'Schliesszeit eingestellt, aber Space zu.') # max 40 Zeichen
        client.publish('space/status/error', 'Schliesszeit eingestellt, aber Space zu!')
    else:
        display_text(client, 'Space offen bis min %s Uhr' % closetime) # max 40 Zeichen
        client.publish('space/status/closetime', closetime)


def display_text(client, text):
    telnet(text)
    client.publish('display/ledlaufschrift/text', text)


def mqtt_received(client, data, msg):
    opentopic = 'space/status/open'
    if msg.topic == opentopic:
        if msg.payload.decode('utf8') != 'true':
            log.info('Space closed, reset wielange time info.')
            write_json(None)
        else:
            log.info('Space opened, reset wielange time info.')
            write_json(None)
            display_text(client, b'Space offen, bitte zeit setzen') # max 40 Zeichen
        return
    log.info('Received msg from wiebis: {}, containing {}'.format(
                msg.topic, msg.payload))
    value = int(msg.payload)
    hours = value // 100
    minutes = value - (hours * 100)
    if msg.topic.endswith('biswann'):
        # uhrzeit
        ctime = datetime.time(hours, minutes).strftime('%H:%M')
        set_output(client, ctime)
        write_json(ctime)
    elif msg.topic.endswith('wielange'):
        # stunden:minuten ab jetzt
        fromnow = datetime.timedelta(hours=hours, minutes=minutes)
        closedt = datetime.datetime.now() + fromnow
        ctime = closedt.strftime('%H:%M')
        set_output(client, ctime)
        write_json(ctime)


mqtt_client.on_message = mqtt_received
mqtt_client.loop_start()


while True:
    curdt = datetime.datetime.now().strftime('%H:%M')
    with open('/home/spaceapi/spaceapi/htdocs/openuntil.json', 'r') as howlong:
        howlongdata = json.loads(howlong.read())
    if curdt == howlongdata['closetime']:
        # time reached, resetting output
        display_text(mqtt_client, 'Schliesszeit erreicht, bitte neu setzen') # max 40 Zeichen
        write_json(None)

    time.sleep(5)

