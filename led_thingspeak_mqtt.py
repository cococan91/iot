import time
import paho.mqtt.client as mqtt
from gpiozero import LED
from bottle import route, run, template, request

# 設置LED
red_led = LED(18)
green_led = LED(23)


# ThingSpeak頻道ID和API Key
channel_id = ""
mqtt_client_id = ""
mqtt_client_username = ""
mqtt_client_password = ""

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,mqtt_client_id)

client.username_pw_set(mqtt_client_username, mqtt_client_password)
client.connect("mqtt3.thingspeak.com", 1883, 60)

# LED狀態列表
leds = {'red': red_led, 'green': green_led}
states = {'red': False, 'green': False}

def update_leds(led):
    red_state = int(states['red'])
    green_state = int(states['green'])
    payload = f"field1={red_state}&field2={green_state}"
    client.publish(f"channels/{channel_id}/publish", payload)
    if states[led]:
        leds[led].on()
    else:
        leds[led].off()
    print("{}: {}".format(led, leds[led].is_lit))    
    print(f"Data uploaded to ThingSpeak: {payload}")

@route('/')
def index():
    return template('''
        <h1>LED Control(thingspeak免費版，上傳間隔15秒)</h1>
        <p>點擊按鈕可控制對應顏色LED燈，需將狀態上傳成功後才更新硬體狀態，故每15秒才能動作一次</p>
        <p>透過MQTT更新狀態無法獲得thingspeak回饋，所以無法確保前端狀態更新才改變硬體狀態</p>
        <form action="/toggle" method="post">
            <input type="submit" name="led" value="red"/>
            <input type="submit" name="led" value="green"/>
        </form>
        ''')

@route('/toggle', method='POST')
def toggle_led():
    led = request.forms.get('led')
    states[led] = not states[led]
    update_leds(led)
    return index()

# 啟動Bottle伺服器
run(host='0.0.0.0', port=8080)
