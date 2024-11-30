from bs4 import BeautifulSoup
import datetime
import time
import configparser
import pathlib
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from paho.mqtt import client as mqtt_client

config_path = pathlib.Path(__file__).parent.absolute() / "config" / "config.cfg"
config = configparser.ConfigParser()
config.read(config_path, encoding='utf-8')

broker = str(config.get('CONFIG', 'broker'))
port = int(config.get('CONFIG', 'port'))
mqttusername = str(config.get('CONFIG', 'mqttusername'))
mqttpassword = str(config.get('CONFIG', 'mqttpassword'))
location = str(config.get('CONFIG', 'location'))
freq = int(config.get('CONFIG', 'freq'))
toplousername = str(config.get('CONFIG', 'toplousername'))
toplopassword = str(config.get('CONFIG', 'toplopassword'))

service = Service()
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-search-engine-choice-screen')
options.add_argument('--disable-gpu')
options.add_argument("--disable-cache")
options.add_argument('--no-sandbox')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--disable-dev-shm-usage')

url = "https://my.toplo.bg/monitoring"
client_id = f'mqtttoplofikaciya'
topic0 = "homeassistant/sensor/toplofikaciya/availability"
topic1 = "homeassistant/sensor/toplofikaciya/location"
topic2 = "homeassistant/sensor/toplofikaciya/tempheating"
topic3 = "homeassistant/sensor/toplofikaciya/temphotwater"
topic4 = "homeassistant/sensor/toplofikaciya/heatmeterenergy"
topic5 = "homeassistant/sensor/toplofikaciya/heatmeterdebit"
topic6 = "homeassistant/sensor/toplofikaciya/heatmeterpower"
topic7 = "homeassistant/sensor/toplofikaciya/dateandtime"
topic8 = "homeassistant/sensor/toplofikaciya/tempwall"
availability = 0
tempheating = 'unknown'
temphotwater = 'unknown'
heatmeterenergy = 'unknown'
heatmeterdebit = 'unknown'
heatmeterpower = 'unknown'
tempwall = 'unknown'
dateandtime = 'unknown'


while True:
    print('Starting new cycle! '+str(datetime.datetime.now())[0:-7]+'\n')
    browser = webdriver.Chrome(service=service, options=options)
    browser.delete_all_cookies()
    page = browser.get(url)
    time.sleep(1)
    browser.refresh()
    wait = WebDriverWait(browser, timeout=10).until(EC.presence_of_element_located((By.ID, "email")))
    browser.find_element("id","email").send_keys(toplousername)
    browser.find_element("id","password").send_keys(toplopassword)
    browser.find_element("xpath", "/html/body/div[1]/div/div/div/div/form/div[4]/button[1]").click()
    time.sleep(3)
    html = browser.page_source
    soup = BeautifulSoup(html.encode('utf-8'), 'html.parser')
    #print(soup)

    counter = 0
    for div in soup.find_all('div', {'class': 'station-tile-title'},limit = 5):
        if location in div:
            counter+=1
            availability = 1
            tempheating = str(div.find_next('div', {'class': 'station-tile-body'}).find_next('div', {'class': 'parameter-value'})).replace('<div class="parameter-value">','').replace('</div>','').replace(",",".").replace(" °C","").replace("-","unknown")
            temphotwater = str(div.find_next('div', {'class': 'station-tile-body'}).find_next('div', {'class': 'parameter-value'}).find_next('div', {'class': 'parameter-value'})).replace('<div class="parameter-value">','').replace('</div>','').replace(",",".").replace(" °C","").replace("-","unknown")
            heatmeterenergy = str(div.find_next('div', {'class': 'station-tile-body'}).find_next('div', {'class': 'parameter-value'}).find_next('div', {'class': 'parameter-value'}).find_next('div', {'class': 'parameter-value'})).replace('<div class="parameter-value">','').replace('</div>','').replace("[","").replace("]","").replace(",",".").replace(" MWh","").replace("-","unknown")
            heatmeterdebit = str(div.find_next('div', {'class': 'station-tile-body'}).find_next('div', {'class': 'parameter-value'}).find_next('div', {'class': 'parameter-value'}).find_next('div', {'class': 'parameter-value'}).find_next('div', {'class': 'parameter-value'})).replace('<div class="parameter-value">','').replace('</div>','').replace("[","").replace("]","").replace(",",".").replace(" l/h","").replace("-","unknown")
            heatmeterpower = str(div.find_next('div', {'class': 'station-tile-body'}).find_next('div', {'class': 'parameter-value'}).find_next('div', {'class': 'parameter-value'}).find_next('div', {'class': 'parameter-value'}).find_next('div', {'class': 'parameter-value'}).find_next('div', {'class': 'parameter-value'})).replace('<div class="parameter-value">','').replace('</div>','').replace("[","").replace("]","").replace(",",".").replace(" kW","").replace("-","unknown")
            dateandtime = str(div.find_next('div', {'class': 'station-tile-footer'})).replace('<div class="station-tile-footer">','').replace('</div>','').replace("-","01.01.1970 00:00")
            print('Location: '+location)
            print('Temp. Heating: '+tempheating+'°C')
            print('Temp. Hot Water: '+temphotwater+'°C')
            print('Heatmeter Energy: '+heatmeterenergy+' MWh')
            print('Heatmeter Debit: '+heatmeterdebit+' l/h')
            print('Heatmeter Power: '+heatmeterpower+' kW')
            xpath = str("/html/body/div[1]/div/section/div/div/div[2]/div[")+str(counter)+str("]/div[1]")
            browser.find_element("xpath", xpath).click()
            time.sleep(3)
            html_mnenoshema = browser.page_source
            soup_mnemoshema = BeautifulSoup(html_mnenoshema.encode('utf-8'), 'html.parser')
            tempwall = str(soup_mnemoshema.select('span[title="Температура външна"]')).replace('[<span data-placement="25;" data-toggle="Температура външна" style="top:25px; left:920px; position:absolute; width:auto; white-space:nowrap" title="Температура външна">','').replace('</span>]','').replace("°C","").replace('--','unknown')
            print('Temp. Wall: '+tempwall+'°C')
            print('Date & Time: '+dateandtime+'\n\n')
        else:
            counter+=1
    if availability == 0:
        tempheating = 'unknown'
        temphotwater = 'unknown'
        heatmeterenergy = 'unknown'
        heatmeterdebit = 'unknown'
        heatmeterpower = 'unknown'
        tempwall = 'unknown'
        dateandtime = 'unknown'
        print('Location: '+location)
        print('Temp. Heating: '+tempheating)
        print('Temp. Hot Water: '+temphotwater)
        print('Heatmeter Energy: '+heatmeterenergy)
        print('Heatmeter Debit: '+heatmeterdebit)
        print('Heatmeter Power: '+heatmeterpower)
        print('Temp. Wall: '+tempwall)
        print('Date & Time: '+dateandtime+'\n\n')
            
    # Generate a Client ID with the publish prefix.
    msg0 = availability
    msg1 = location
    msg2 = tempheating
    msg3 = temphotwater
    msg4 = heatmeterenergy
    msg5 = heatmeterdebit
    msg6 = heatmeterpower
    msg7 = dateandtime
    msg8 = tempwall

    browser.close()
    browser.quit()

    def connect_mqtt():
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)
        client.username_pw_set(mqttusername, mqttpassword)
        client.on_connect = on_connect
        client.connect(broker, port)
        return client

    def publish(client):
        client.publish(topic0, msg0, retain=False)
        client.publish(topic1, msg1)
        client.publish(topic2, msg2)
        client.publish(topic3, msg3)
        client.publish(topic4, msg4)
        client.publish(topic5, msg5)
        client.publish(topic6, msg6)
        client.publish(topic7, msg7)
        client.publish(topic8, msg8)

    def on_disconnect(client, userdata, rc):
        logging.info("Disconnected with result code: %s", rc)
        reconnect_count, reconnect_delay = 9, FIRST_RECONNECT_DELAY
        while reconnect_count < MAX_RECONNECT_COUNT:
            logging.info("Reconnecting in %d seconds...", reconnect_delay)
            time.sleep(reconnect_delay)

            try:
                client.reconnect()
                logging.info("Reconnected successfully!")
                return
            except Exception as err:
                logging.error("%s. Reconnect failed. Retrying...", err)

            reconnect_delay *= RECONNECT_RATE
            reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
            reconnect_count += 1
        logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)
        global FLAG_EXIT
        FLAG_EXIT = True
    
    def run():
        try:
            client = connect_mqtt()
            publish(client)
            client.on_disconnect = on_disconnect
        except:
            return


    if __name__ == '__main__':
        run()

    
    print('Cycle done! '+str(datetime.datetime.now())[0:-7]+'\n')
    print('Next cycle starts in '+str(freq)+' seconds.'+'\n\n\n')
    for i in range(freq):
        time.sleep(1)
