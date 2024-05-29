import time
import thingspeak
from gpiozero import LED
from bottle import route, run, template, request

# 設置LED
red_led = LED(18)
green_led = LED(23)

# ThingSpeak頻道ID和API Key
channel_id = ""
write_key = ""

# 初始化ThingSpeak頻道
channel = thingspeak.Channel(id=channel_id, api_key=write_key)

# LED狀態列表
leds = {'red': red_led, 'green': green_led}
states = {'red': False, 'green': False}

def update_leds(led):
    response = channel.update({'field1': int(states['red']), 'field2': int(states['green'])})
    print(f"Data uploaded to ThingSpeak: {response}")
    #檢查是否有上傳成功後再修改硬體狀態
    if response != '0':
        if states[led]:
            leds[led].on()
        else:
            leds[led].off()
        #顯示修改過後LED狀態    
        print("{}: {}".format(led, leds[led].is_lit))

@route('/')
def index():
    return template('''
        <h1>LED Control(thingspeak免費版，上傳間隔15秒)</h1>
        <p>點擊按鈕可控制對應顏色LED燈，需將狀態上傳成功後才更新硬體狀態，故每15秒才能動作一次</p>
        <p>此限制是為確保前後端狀態一致，如有需要可自行修改程式碼，只需把檢查thingspeak回應內容的判斷式移除或改為永遠成立</p>
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
