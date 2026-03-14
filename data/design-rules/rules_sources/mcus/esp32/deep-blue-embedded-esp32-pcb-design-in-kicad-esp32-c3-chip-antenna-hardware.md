---
source: "Deep Blue Embedded -- ESP32 PCB Design in KiCAD (ESP32-C3 + Chip Antenna Hardware Design)"
url: "https://deepbluembedded.com/esp32-pcb-design-in-kicad-esp32-c3-chip-antenna-hardware-design/"
format: "HTML"
method: "readability"
extracted: 2026-03-02
chars: 19620
---

In this article, I’ll show you the ESP32 schematic & PCB design steps to make your own custom ESP32-C3 PCB board. I’ll explain some of the design decisions I’ve made, how to prepare the files needed for manufacturing, and how to place the PCB SMT order at JLCPCB, who are kindly sponsoring this project.

This is a custom development board designed for evaluating the Raspberry Pi Pico2 RP2350 MCU with an ESP32-C3 for WiFi/BLE connectivity. This project can serve as a baseline for anyone willing to create their own custom dev board based on the RP2350 or ESP32-C3 microcontrollers.

This Project is Sponsored By **[JLCPCB](https://jlcpcb.com/?from=deepbluembedded)**

## Table of Contents

1. [ESP32 Hardware Design Overview](#esp32-hardware-design-overview)
2. [ESP32-C3 Schematic Design](#esp32c3-schematic-design)
3. [ESP32-C3 + Chip Antenna PCB Layout & Routing](#esp32c3-chip-antenna-pcb-layout-amp-routing)
4. [Placing PCBA Order @ JLCPCB](#placing-pcba-order-jlcpcb)
5. [Getting Started With ESP32 (Arduino IDE)](#getting-started-with-esp32-arduino-ide)
6. [ESP32 LED Blinking GPIO Example](#esp32-led-blinking-gpio-example)
7. [ESP32 USB CDC Serial Printf Example](#esp32-usb-cdc-serial-printf-example)
8. [ESP32 WS2812 Neopixel RGB Example](#esp32-ws2812-neopixel-rgb-example)
9. [ESP32 BLE (Bluetooth Low-Energy) Demo Example](#esp32-ble-bluetooth-lowenergy-demo-example)
10. [ESP32 WiFi Scan & Connect Example](#esp32-wifi-scan-amp-connect-example)
11. [ESP32 WebServer Demo Example](#esp32-webserver-demo-example)
12. [RP2350 + ESP32-C3 WiFi WebServer Demo Example](#rp2350-esp32c3-wifi-webserver-demo-example)
13. [Wrap Up](#wrap-up)
14. [[YouTube Video] ESP32-C3 PCB Design Project](#youtube-video-esp32c3-pcb-design-project)

---

## **ESP32 Hardware Design Overview**

This PCB project features an RP2350B microcontroller for evaluation and development purposes, and it also has an ESP32-C3 with a chip antenna onboard to provide WiFi/BLE connectivity over an SPI bus between the RP2350 & ESP32-C3 microcontrollers.

In this project article, we’ll address the (ESP32-C3 + chip antenna) hardware design aspect of the project, as we’ve previously covered the **[RP2350 Hardware Design](https://deepbluembedded.com/rp2350-hardware-pcb-design-in-kicad-rp2350-schematic/)** part in a previous project.

### **ESP32-C3 Overview**

The ESP32-C3 is a low-power MCU of the ESP32 family that has a RISC-V core @ 160MHz, 2.4GHz WiFi, and Bluetooth low-energy (BLE). It has plenty of peripherals (like Timers, PWMs, ADC, UART, SPI, I2C, and I2S), and even an integrated flash memory in some variants. So it’s a highly integrated solution that suits a wide variety of applications.

The functional block diagram of the ESP32-C3 SoC is shown below.

### **ESP32-C3 Variants**

There are four variants for the ESP32-C3 microcontroller, only two of which are recommended for new designs: ESP32-C3FH4 & ESP32-C3FH4X. Both have internal 4MB of flash memory, the same package size, but the usable GPIO pin count is 16 or 22.

Here is a brief comparison table for the major differences between those devices:

### **ESP32-C3 Hardware Design Guidelines & Datasheet**

To design a custom ESP32-based PCB project, we’ll need to reference the documents below.

**[ESP32-C3 Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf)**

**[ESP32-C3 Mini Reference Design](https://www.espressif.com/sites/default/files/documentation/esp32-c3-mini-1_datasheet_en.pdf)**

**[ESP32-C3 Hardware Design Guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/esp-hardware-design-guidelines-en-master-esp32c3.pdf)**

---

## **ESP32-C3 Schematic Design**

This is the schematic design that I came up with for this ESP32-C3 development board project. Some parts are not mandatory and can be omitted for even more cost optimization if needed.

### **1. DC PWR In + LDO + USB**

There’s a USB-C port that I’m using for power input (+5V) as well as USB CDC communication and programming for the ESP32-C3 microcontroller.

The USB +5V input is regulated down to 3.3V using an LDO. The +3.3V is then used to power up the ESP32-C3 microcontroller.

### **2. ESP32-C3 MCU Circuitry + Chip Antenna**

The ESP32-C3 requires a few decoupling capacitors for the digital 3.3V power rails (**VDD** & **VDDA**). Note that the analog power input is called **VDD\_3P3**, and it requires an inductor + 2 capacitors pi filter.

The ESP32-C3FH4 variant has an internal QSPI flash memory on-chip; no need to connect an external QSPI flash memory. However, the QSPI interface pins are not usable even though.

I’ve also added a **RESET** button to reset the microcontroller when needed. And we’ll need it every time we try to flash a new firmware to the chip. For USB programming, a **BOOT** button is also needed on the GPIO9 line while pulling up the GPIO8 pin.

### **3. Strapping (Boot) Pins**

At each startup or reset, a chip requires some initial configuration parameters, such as: in which boot mode to load the chip, etc. These parameters are passed over via the strapping (boot) pins. After reset, the strapping pins work as normal function pins. GPIO2, GPIO8, and GPIO9 are strapping pins.

After a chip reset, the combination of GPIO2, GPIO8, and GPIO9 controls the boot mode according to the table below.

Note that: GPIO2 actually does not determine SPI Boot and Joint Download Boot mode, but it is recommended to pull this pin up due to glitches.

Joint Download Boot mode supports the following download methods:

* USB-Serial-JTAG Download Boot
* UART Download Boot

### **4. Chip Antenna + Matching Network**

For this board, I’ve used a chip antenna part (ANT3216LL00R2400A) with an LC Pi matching network. If you’re not sure about the values to use, you can use a 0Ω resistor instead of the inductor (L) and DNP (do not place) the 2 capacitors to try different values until you get a “good” matching.

Note: Do yourself a favor and use at least 0603 parts for the matching network to make your life easier while playing around with different values. I do regret using 0402s for this.

### **5. IO Port + LEDs**

Just pin out all the IO pins you need to one or two headers, depending on your desired board shape and layout.

For my board, I’ve added a power indicator LED + 1x user-programmable LED + 1x NeoPixel RGB LED (WS2812B).

---

## **ESP32-C3 + Chip Antenna PCB Layout & Routing**

The PCB layout & routing for this ESP32-C3 dev board is really straightforward. You just need to place the decoupling capacitors as close as possible to the power pins of the ESP32 chip.

Route your USB **90Ω** differential pair from the connector straight to the chip and place the 22Ω termination resistors as close as possible to the ESP32 chip’s USB pins.

Last and most importantly, the RF section for the chip antenna. For this, you’ll need to route the **LNA\_IN** RF output pin through a **50Ω** trace to the antenna matching network and then to the antenna’s feed point. It’s highly recommended to use a “**Rounded Track**” for your 2.4GHz RF output line, which is very easy to do in KiCAD using the RF toolkit plugin.

Below is the recommended layout from the antenna’s datasheet.

And this is exactly what I’ve done on my board.

---

## **Placing PCBA Order @ JLCPCB**

Finally, we’re ready to generate the fabrication files and send them to JLCPCB for PCB fabrication and assembly. For this task, I use the KiCAD plugin named “Fabrication Toolkit”. With just one button click, you’ll have all manufacturing output files ready in a new folder that’s automatically created for you by the plugin toolkit.

### **1. Upload Your Gerber File & Check PCB Fab. Options**

The next step is to upload your PCB Gerber files and modify the PCB fabrication options as needed in your project. Just keep an eye on the price because some options are not considered as a standard fabrication process, which will end up costing you a bit more and take a bit more time to get fabricated.

Even if you’re 100% sure that your design & fabrication files are flawless, the online system & JLCPCB or any other fab house can still pick up incorrect components’ orientation or placement. Always double-check the PCB component placement after uploading your files.

### **2. Upload BOM & CPL Files**

The next step is to upload your design’s BOM file and the components positions file (CPL) to JLCPCB and let it check the files and report the stock status and total number of components to be assembled, their cost, and so on.

Check everything and make sure the components are selected correctly from the JLCPCB SMT library. And also double-check the component placements on the next page and correct any wrong rotations in the CPL file. There is a mismatch between the KiCAD output position file & JLCPCB’s system, so it does pick up wrong orientations for some ICs, diodes, etc. Always double-check everything before placing the order.

### **3. Pay To Place Your Order**

The last step to place your order is to pay for the invoice, and you can apply any valid discount coupon at this step to reduce the cost.

### **4. Wait For Delivery & Prepare For Testing!**

You should expect to receive your board within 4 days to 1 week, depending on where you live.

Here is how it turned out at the end.

---

## **Getting Started With ESP32 (Arduino IDE)**

To get started with ESP32 microcontroller development in Arduino IDE, you first need to install the ESP32 Arduino Core. The tutorial linked below is a very detailed guide that will help you get started with Arduino C++ development for the ESP32 microcontrollers.

This is a guide for getting started with ESP32 using Arduino IDE. You’ll learn how to install the ESP32 Arduino Core, create a new project, and build/flash your firmware projects to ESP32 boards from the Arduino IDE.

You can, however, use MicroPython, CircuitPython, ESP-IDF (RTOS-based) C SDK, Rust, or any other alternative development environment that you prefer to use.

For the bring-up testing of the ESP32-C3 PCB project, I’ll be using Arduino IDE to write some firmware demo examples to test our custom hardware dev board.

---

## **ESP32 LED Blinking GPIO Example**

This is the first test example project in which we’ll blink the onboard LED attached to the GPIO8 pin.

We’ll just turn the LED ON/OFF for 100ms each.

### **ESP32 LED Blinking GPIO Example Code**

**The Application Code For This Example**

```
/*
 * LAB Name: ESP32-C3 GPIO Demo
 * Author: Khaled Magdy
 * For More Info Visit: www.DeepBlueMbedded.com
*/
void setup() {
  pinMode(8, OUTPUT);
}

void loop() {
  digitalWrite(8, HIGH);
  delay(100);
  digitalWrite(8, LOW);
  delay(100);
}
```

Compile & Flash the firmware to the board using the USB bootloader. Here are my Arduino ESP32 board configuration options:

### **ESP32 LED Blinking Test Result**

---

## **ESP32 USB CDC Serial Printf Example**

In this test project, we’ll do serial print using USB CDC with the ESP32-C3 microcontroller in Arduino IDE.

Note: You need to have “USB CDC Enabled after boot” from the Arduino > Tools > Board options list.

### **ESP32 USB CDC Serial Print Example Code**

**The Application Code For This Example**

```
/*
 * LAB Name: ESP32-C3 USB CDC Demo
 * Author: Khaled Magdy
 * For More Info Visit: www.DeepBlueMbedded.com
*/
void setup() {
  Serial.begin(115200);
}

void loop() {
  Serial.println("Hello From ESP32-C3!");
  delay(500);
}
```

Compile & Flash the firmware to the board using the USB bootloader.

### **ESP32 USB CDC Serial Print Test Result**

---

## **ESP32 WS2812 Neopixel RGB Example**

In this test project, we’ll do a simple RGB color effect with the onboard WS2812 Neopixel RGB LED connected to our ESP32-C3 microcontroller.

For this demo, I’ll use the FastLED Arduino library to control my WS2812 Neopixel RGB LED.

### **ESP32 WS2812 Neopixel RGB Example Code**

**The Application Code For This Example**

```
/*
 * LAB Name: ESP32-C3 WS2812 Neopixel RGB LED Example
 * Author: Khaled Magdy
 * For More Info Visit: www.DeepBlueMbedded.com
*/
#include

#define LED_PIN     5
#define NUM_LEDS    1
#define BRIGHTNESS  100
#define LED_TYPE    WS2812B
#define COLOR_ORDER GRB

CRGB led[NUM_LEDS];

void setup() {
  FastLED.addLeds(led, NUM_LEDS);
  FastLED.setBrightness(BRIGHTNESS);
}

void loop() {
  static uint8_t hue = 0;
  led[0] = CHSV(hue++, 255, 255); // Cycle through hues
  FastLED.show();
  delay(20);  // Adjust for speed of color change
}
```

Compile & Flash the firmware to the board using the USB bootloader.

### **ESP32 WS2812 Neopixel RGB Test Result**

---

## **ESP32 BLE (Bluetooth Low-Energy) Demo Example**

In this test project, we’ll control the Neopixel RGB LED color using BLE (Bluetooth Low Energy) communication between our ESP32-C3 custom dev board and a smartphone with the nRF Connect BLE Android app.

### **ESP32 BLE Example Code**

```
/*
 * LAB Name: ESP32-C3 BLE + Neopixel RGB LED Example
 * Author: Khaled Magdy
 * For More Info Visit: www.DeepBlueMbedded.com
*/
#include
#include
#include
#include
#include

#define LED_PIN     5
#define NUM_LEDS    1
#define BRIGHTNESS  100
#define LED_TYPE    WS2812B
#define COLOR_ORDER GRB

CRGB led[NUM_LEDS];

// UUIDs for BLE service and characteristic
#define SERVICE_UUID        "d3aa0001-8e9f-4e38-a4f3-9999d61b1c90"
#define CHARACTERISTIC_UUID "d3aa0002-8e9f-4e38-a4f3-9999d61b1c90"

BLECharacteristic *pCharacteristic;

class MyCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pCharacteristic) {
    String rxValue = pCharacteristic->getValue();
    if (rxValue.length() > 0) {
      Serial.print("Received: ");
      Serial.println(rxValue);

      int r = 0, g = 0, b = 0;
      sscanf(rxValue.c_str(), "%d,%d,%d", &r, &g, &b);

      led[0] = CRGB(r, g, b);
      FastLED.show();
    }
  }
};

void setup() {
  Serial.begin(115200);

  // FastLED setup
  FastLED.addLeds(led, NUM_LEDS);
  FastLED.setBrightness(BRIGHTNESS);
  led[0] = CRGB::Black;
  FastLED.show();

  // BLE setup
  BLEDevice::init("ESP32C3-RGB");
  BLEServer *pServer = BLEDevice::createServer();
  BLEService *pService = pServer->createService(SERVICE_UUID);

  pCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_WRITE |
    BLECharacteristic::PROPERTY_READ
  );

  pCharacteristic->setCallbacks(new MyCallbacks());
  pCharacteristic->addDescriptor(new BLE2902());
  pCharacteristic->setValue("0,0,0");  // Initial RGB value

  pService->start();

  // BLE advertising with proper configuration
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(false);
  pAdvertising->setMinPreferred(0x06);  // Recommended connection parameters
  pAdvertising->setMaxPreferred(0x12);
  BLEDevice::startAdvertising();

  Serial.println("BLE RGB LED Controller Started. Connect and send RGB values (e.g., 255,0,0).");
}

void loop() {
  // No action needed here; BLE callbacks handle updates
}
```

### **ESP32 BLE Example Test Result**

Here I’m sending pre-saved color messages from my smartphone (nRF Connect BLE) app to our ESP32-C3 custom dev board to control the RGB LED color.

---

## **ESP32 WiFi Scan & Connect Example**

In this test project, we’ll scan for nearby WiFi networks and connect our ESP32-C3 board to my home router’s WiFi network.

### **ESP32 WiFi Scan & Connect Example Code**

```
/*
 * LAB Name: ESP32-C3 WiFi Scan Example
 * Author: Khaled Magdy
 * For More Info Visit: www.DeepBlueMbedded.com
*/
#include

const char* ssid = "Your_SSID";
const char* password = "Your_Password";

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("Starting Wi-Fi Scan...");

  // Set WiFi to station mode and disconnect from any AP
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);
  // WiFi Scan
  Serial.println("Scanning for Wi-Fi networks...");
  int n = WiFi.scanNetworks();
  if (n == 0) {
    Serial.println("No networks found");
  } else {
    Serial.println("Networks found:");
    for (int i = 0; i < n; ++i) {
      Serial.print(i + 1);
      Serial.print(": ");
      Serial.print(WiFi.SSID(i));
      Serial.print(" (RSSI: ");
      Serial.print(WiFi.RSSI(i));
      Serial.print(" dBm, ");
      Serial.print("Encryption: ");
      Serial.print(WiFi.encryptionType(i));
      Serial.println(")");
      delay(10);
    }
  }
  // WiFi Connect
  WiFi.begin(ssid, password);
  Serial.print("Connecting to (Khaled Net) Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi Connected!");
  Serial.print("Access at: http://");
  Serial.println(WiFi.localIP());
}

void loop() {

}
```

### **ESP32 WiFi Scan & Connect Example Test Result**

Here is the result of running this demo test. My home WiFi network is the strongest signal found, as expected, and we could successfully connect to it and get an IP address.

---

## **ESP32 WebServer Demo Example**

In this test project, we'll connect our ESP32-C3 to a home network and set it up as a web server that hosts a webpage with a slider to allow any user on the network to access the webpage and control the onboard LED's brightness with the slider.

### **ESP32 WebServer Example Code**

```
/*
 * LAB Name: ESP32-C3 WiFi WebServer Example
 * Author: Khaled Magdy
 * For More Info Visit: www.DeepBlueMbedded.com
*/
#include
#include

const char* ssid = "Your_SSID";
const char* password = "Your_Password";

WebServer server(80);
const int ledPin = 8;
int brightness = 0;

void handleRoot() {
  server.send(200, "text/html", R"rawliteral(










  )rawliteral");
}

void handleSet() {
  if (server.hasArg("value")) {
    brightness = server.arg("value").toInt();
    analogWrite(ledPin, abs(brightness-255));
    //Serial.printf("Brightness set to %d\n", brightness);
    server.send(200, "text/plain", "OK");
  } else {
    server.send(400, "text/plain", "Bad Request");
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(ledPin, OUTPUT);
  analogWrite(ledPin, 255);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500); Serial.print(".");
  }
  Serial.println("\nConnected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  server.on("/", handleRoot);
  server.on("/set", handleSet);
  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient();
}
```

### **ESP32 WebServer Example Test Result**

Here I am controlling the onboard LED's brightness from a webpage on our ESP32-C3 webserver.

---

## **RP2350 + ESP32-C3 WiFi WebServer Demo Example**

Before concluding this project, let's take a look at a quick demo example for the ESP32-C3 acting as a WebServer that allows the user to access a webpage to select a desired color, then sends the data over SPI to the RP2350 that displays it to a Neopixel RGB LED.

---

## **Wrap Up**

By the end of this project, you should have learned how to create your custom ESP32-C3 dev board or incorporate this microcontroller in your next project to provide WiFi/Bluetooth connectivity. We have also discussed how to bring up your custom ESP32-based hardware design using the Arduino IDE.

We've already covered the **[RP2350 Hardware Design](https://deepbluembedded.com/rp2350-hardware-pcb-design-in-kicad-rp2350-schematic/)** part of this project in a previous tutorial, if you'd like to check it out as well.

## **[YouTube Video] ESP32-C3 PCB Design Project**

### *Related*