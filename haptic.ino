#include "Arduino.h"
#include "WiFi.h"
#include <OSCMessage.h>

WiFiUDP Udp;  // A UDP instance to let us send and receive packets over UDP
int LED_BUILTIN = 13; // This pin controls the vibration motor

int update_rate = 30; // update rate. 30 is about 33Hz

// Network settings
char ssid[] = "your ssid";       // your network SSID (name)
char pass[] = "your password";  // your network password
unsigned int localPort = 8888;  // local port to listen for OSC packets

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);

  /* setup wifi */
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
  Udp.begin(localPort);
  // Serial.print("connected to WIFI");
  // Serial.print("IP address: ");
  // Serial.println(WiFi.localIP());
}

void ledtoggle(OSCMessage &msg) {
  int a = msg.getBoolean(0);
  if (a == false) {
    digitalWrite(LED_BUILTIN, LOW);
  } else if (a == true) {
    digitalWrite(LED_BUILTIN, HIGH);
  } else {
    //   Serial.println("Unknown message!");
  }
}

void receiveMessage() {
  OSCMessage inmsg;
  int size = Udp.parsePacket();

  if (size > 0) {
    while (size--) {
      inmsg.fill(Udp.read());
    }
    if (!inmsg.hasError()) {
      inmsg.dispatch("/avatar/parameters/Tail_IsGrabbed", ledtoggle);
    }
    //else { auto error = inmsg.getError(); }
  }
}

void loop() {
  receiveMessage();
  delay(update_rate);
}