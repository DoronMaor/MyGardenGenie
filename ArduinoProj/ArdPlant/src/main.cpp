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
#define LED_SCREEN_PIN            2
#define WATER_PUMP_RELAY_PIN_A    4
#define WATER_PUMP_RELAY_PIN_B    3
#define LED_PIN_A                 6
#define LED_PIN_B                 7
#define LIGHT_SENS_PIN_A          A0
#define MOISTURE_PIN_A            A2
#define MOISTURE_PIN_B            A3

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
  }
  else if (type=='B'){
    // Active low relay
    digitalWrite(WATER_PUMP_RELAY_PIN_B, LOW);
    delay(dur);
    digitalWrite(WATER_PUMP_RELAY_PIN_B, HIGH);
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
  Serial.println(" lx");


  return lux;
}

const bool testingMode = true;

void loop() {

  if (testingMode)
  {
    int ma = GetMoisture('A');
    int mb = GetMoisture('B');
    float l = GetLightSensor();
    WriteToLCD("MoisA: " + String(ma) + "|" + "MoisB: " + String(mb)+ "|" + "Light: " + String(l));

    TurnPump(800, 'A');
    TurnPump(800, 'B');  
    
    TurnLEDRing(true, 'A');
    TurnLEDRing(true, 'B');

    
      
    if (false)
    {
      float l = GetLightSensor();
      WriteToLCD("Light: " + String(l));
      TurnPump(800, 'A');
      TurnPump(800, 'B');  
      TurnLEDRing(true, 'A');
      TurnLEDRing(true, 'B');
    }
    delay(1000);
  }
  else {
    if (Serial.available() > 0){
      String msg = Serial.readStringUntil('\n');

      if (msg.substring(0, 5) == "#LCD#")
      {
      // #LCD#text
          WriteToLCD(msg.substring(5));
      }
      else if (msg.substring(0, 9) == "#MOISTURE#")
      {
        //#GET_MOISTURE#A/B
        char plant = msg.substring(9)[0];
        int mois = GetMoisture(plant);
        Serial.print("#MOISTURE#" + mois);
      }
      else if (msg.substring(0, 7) == "#LIGHT#")
      {
        //#GET_LIGHT#
        int light = GetLightSensor();
        Serial.print("#LIGHT#" + light);
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
            Serial.print("ERROR" + msg);
        }
    }
  }


/*
  if (Serial.available() > 0){
    String msg = Serial.readStringUntil('\n');

    if (msg.substring(0, 5) == "#LCD#")
    {
    // #LCD#text
        WriteToLCD(msg.substring(5));
    }
  else if (msg.substring(0, 9) == "#MOISTURE#")
  {
    //#GET_MOISTURE#A/B
    String plant = msg.substring(9);
    int mois = GetMoisture(plant);
    Serial.print("#MOISTURE#" + m.ToString());
  }
  else if (msg.substring(0, 7) == "#LIGHT#")
  {
    //#GET_LIGHT#A/B
    String m = msg.substring(7);
    int mois = GetLightSensor(m);
    Serial.print("#LIGHT#" + m.ToString());
  }
  else if (msg.substring(0, 8) == "#T_PUMP#")
  {
    //#T_PUMP#10/[time];A/B
    String m = msg.substring(8);
    TurnPump((int)(m[0] + m[1]), m.substring(2));
  }
  else if (msg.substring(0, 11) == "#T_LEDRING#")
  {
    //#T_LEDRING#0/1;A/B
    String m = msg.substring(11);
    if (m[0] == '0')
      TurnLEDRing(true, m.substring(2));
    else if (m[0] == '1')
      TurnLEDRing(false, m.substring(2));
  }
    else
    {
        Serial.print("ERROR" + msg);
    }
  }*/

}