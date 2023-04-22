#include <Arduino.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <String.h>
#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif
#include <BH1750.h>

/*
  HARDWARE & COMPONENTS LIST:
    + LED RINGx2 [] [5v] *
    + LED SCREENx1 [] [3v]
    + WATER PUMPx2 [] [12v - batteries] *
      # RELAYx2 [] [5v]
      # BATTERIES HOLDER
    + MOISTUREx2 [] *
      # COMPARATORx2 [3v] *
    + LIGHT SENSORx2 [5v] *
    + MINI-BREADBOARD
*/

// Define pins
// #define LED_SCREEN_PIN            2 // [orange->main SCL] [white->main SDL]
#define WATER_PUMP_RELAY_PIN_A    9 // [purple->9] [gray->ground] [black->5v]
#define WATER_PUMP_RELAY_PIN_B    8 // [purple->8] [gray->ground][blue->5v]
#define LED_PIN_A                 10 // [green->ground] [orange->5v] [brown->10]
#define LED_PIN_B                 11 // [green->ground] [red->5v] [brown->11]
#define LIGHT_SENS_PIN_A          A0 // [yellow->5v not connected] [purple->SDA] [blue->SCL] [white->ground]
#define MOISTURE_PIN_A            A2 // [A2->white->A0] [black->ground] [orange->3.3v] comparator [L: blue and gray]
#define MOISTURE_PIN_B            A3 // [A3->yellow->A0] [black->ground] [red->3.3v] comparator [L: yellow and purple]

#define LED_RING_PIXELS     12
const int LED_COLOR[] = {204, 51, 255};

// Hardware objects
Adafruit_NeoPixel ledRingA(LED_RING_PIXELS, LED_PIN_A, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel ledRingB(LED_RING_PIXELS, LED_PIN_B, NEO_GRB + NEO_KHZ800);

LiquidCrystal_I2C lcd(0x3f, 16, 2);

// light sens
BH1750 LightMeterA;


/*
  Functions:
    v) TurnLEDRing
    v) WriteToLCD
    x) TurnPump
    v) GetMoisture
    x) GetLightSensor
*/


void setup() {

  Wire.begin();
  // LED screen
  lcd.begin(16, 2);
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.setBacklight(HIGH);

  // LED rings
#if defined(__AVR_ATtiny85__) && (F_CPU == 16000000)
  clock_prescale_set(clock_div_1);
#endif
  ledRingA.begin();
  ledRingB.begin();
  ledRingA.clear();
  ledRingB.clear();
  ledRingA.show();
  ledRingB.show();

  //water pump
  pinMode(WATER_PUMP_RELAY_PIN_A, OUTPUT);
  pinMode(WATER_PUMP_RELAY_PIN_B, OUTPUT);
  digitalWrite(WATER_PUMP_RELAY_PIN_A, HIGH);
  digitalWrite(WATER_PUMP_RELAY_PIN_B, HIGH);

  //light sens
  LightMeterA.begin();


  Serial.begin(115200);
}


void WriteToLCD(String text) {
  lcd.backlight();
  lcd.clear();
  int i;
  for (i = 0; text[i] != '\0'; ++i);
  if (i > 16)
  {
    lcd.setCursor(0, 0);
    lcd.print(text.substring(0, 16));
    lcd.setCursor(0, 1);
    lcd.print(text.substring(16));
  }
  else
  {
    lcd.setCursor(0, 0);
    lcd.print(text);
  }
}

void TurnLEDRing(bool mode, char type) {
  if (type == 'A')
  {
    if (mode)
      {
        for (int i = 0; i < LED_RING_PIXELS; i++) {

          ledRingA.setPixelColor(i, ledRingA.Color(LED_COLOR[0], LED_COLOR[1], LED_COLOR[2]));
          ledRingA.show();
        }
    }
    else
    {
      ledRingA.clear();
      ledRingA.show();
    }
  }
  else if (type == 'B')
  {
    if (mode)
      {
        for (int i = 0; i < LED_RING_PIXELS; i++) {

          ledRingB.setPixelColor(i, ledRingA.Color(LED_COLOR[0], LED_COLOR[1], LED_COLOR[2]));
          ledRingB.show();
        }
    }
    else
    {
      ledRingB.clear();
      ledRingB.show();
    }
  }
}

void TurnPump(int dur, char type) {

  if (type=='A'){
    // Active low relay
    digitalWrite(WATER_PUMP_RELAY_PIN_A, LOW);
    delay(dur);
    digitalWrite(WATER_PUMP_RELAY_PIN_A, HIGH);
    delay(3000);
  }
  else if (type=='B'){
    // Active low relay
    digitalWrite(WATER_PUMP_RELAY_PIN_B, LOW);
    delay(dur);
    digitalWrite(WATER_PUMP_RELAY_PIN_B, HIGH);
    delay(3000);
  }
  else {
    digitalWrite(WATER_PUMP_RELAY_PIN_B, HIGH);
    digitalWrite(WATER_PUMP_RELAY_PIN_A, HIGH);
    WriteToLCD("Failed TurnPump");
  }
}

int GetMoisture(char type) {
  int val = -1111;
  if (type == 'A')
    val = analogRead(MOISTURE_PIN_A);
  else if (type== 'B')
    val = analogRead(MOISTURE_PIN_B);

  return val;
}

float GetLightSensor() {
  int l = -1;
  float lux = LightMeterA.readLightLevel();
  Serial.print("Light: ");
  Serial.print(lux);

  return lux;
}

void serialFlush() {
  while (Serial.available() > 0) {
    char ch = Serial.read();
  }
}

const bool testingMode = false;

void loop() {

  if (testingMode)
  {

    int ma = GetMoisture('A');
    int mb = GetMoisture('B');
    float l = GetLightSensor();
    WriteToLCD("MoisA:" + String(ma) + "/" + "MoisB:" + String(mb)+ "/" + "Light:" + String(l));
    //Serial.print("MoisA:" + String(ma) + "/" + "MoisB:" + String(mb)+ "/" + "Light:" + String(l));
    TurnPump(1000, 'A');
    TurnPump(1000, 'B');

    TurnLEDRing(true, 'A');
    TurnLEDRing(true, 'B');
    delay(1000);
  }
  else {
    if (Serial.available() > 0){
      String msg = Serial.readStringUntil('\n');
      // WriteToLCD(msg.substring(0, 9));

      if (msg.substring(0, 5) == "#LCD#")
      {
        // #LCD#text
        WriteToLCD(msg.substring(5));
        serialFlush();
      }
      else if (msg.substring(0, 10) == "#MOISTURE#")
      {
        //#GET_MOISTURE#A/B
        char plant = msg.substring(10)[0];
        int mois = GetMoisture(plant);
        Serial.print("#MOISTURE#" + String(mois));
        delay(100);
      }
      else if (msg.substring(0, 7) == "#LIGHT#")
      {
        //#GET_LIGHT#
        int light = GetLightSensor();
        Serial.print("#LIGHT#" + light);
        delay(100);
      }
      else if (msg.substring(0, 8) == "#T_PUMP#")
      {
        //#T_PUMP#10/[time(len=4)];A/B
        String m = msg.substring(8);
        String t = m.substring(0, 5);
        int dur = t.toInt();
        TurnPump((dur), m[5]);
      }
      else if (msg.substring(0, 11) == "#T_LEDRING#")
      {
        //#T_LEDRING#0/1;A/B
        String m = msg.substring(11);
        bool mode = false;
        String modes = "01";
        if (m[0] == modes[1])
          mode = true;
        TurnLEDRing(mode, m[2]);
      }
        else
        {
          Serial.print("ERROR - " + msg );
        }
    }
  }

}
