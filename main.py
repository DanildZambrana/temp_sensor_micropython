import network, time, ntptime, dht, urequests, gc
from lcd1602 import LCD
from machine import Pin, I2C


# Wi-Fi configuration
SSID = "YESSITALOPEZ 2.4G"  # modify this
PASSWORD = "FAMILY-ZAMLO-2022"  # modify this

# DHT11 and LED configuration
sensor = dht.DHT11(Pin(17))
led = Pin("LED", Pin.OUT)

led.off()

i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)
lcd = LCD(i2c)
lcd.clear()

# Timestamp for periodic tasks
last_update = time.ticks_ms()


# Connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        print("Connecting to WiFi...")
        lcd.write(0, 0, "Connectando a Wi-Fi...")
        lcd.write(0,1, SSID)
        time.sleep(1)
    print("WiFi Connected:", wlan.ifconfig())
    lcd.write(0, 0, "Conectado a Wi-Fi...")
    lcd.write(0, 1, wlan.ifconfig()[0])
    ntptime.settime()

def publish_data(humidity, temperature):
    url = "http://192.168.1.157:3000/api/sensor"
    data = {
        "temperature": temperature,
        "humidity": humidity,
        "timestamp": time.time() + (-6)*3600
    }
    response = None
    try:
        gc.collect()
        response = urequests.post(url, json=data)
        if response.status_code == 201:
            print("Data published successfully.")
        else:
            print(f"Failed to publish data: {response.status_code}")
            response.close()
    except Exception as e:
        print("Error publishing data:", e)
    finally:
        try:
            if response:
                response.close()
        except:
            pass
        gc.collect()

# Main program
def main():
    global last_update

    connect_wifi()

    while True:

        # Update DHT11 data every 10 seconds
        if time.ticks_diff(time.ticks_ms(), last_update) > 10000:
            try:
                sensor.measure()
                temperature = str(sensor.temperature())  # Temperature
                humidity = str(sensor.humidity())  # Humidity

                print(f"Temperature: {temperature}C   Humidity: {humidity}% time: {time.time()}")

                lcd.clear()
                lcd.write(0, 0, f"Temperatura: {temperature}C")
                lcd.write(0, 1, f"Humedad: {humidity}%")
                led.on()
                publish_data(humidity, temperature)
                led.off()

                last_update = time.ticks_ms()  # Update timestamp
            except Exception as e:
                print("Error:", e)
try:
    main()
except Exception as e:
    print("Error:", e)
