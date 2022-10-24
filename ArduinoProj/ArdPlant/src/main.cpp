#include <Arduino.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <String.h>
#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
	#include <avr/power.h>
#endif

/*
	HARDWARE LIST:
		+ LED RINGx2 [1:2-D] [5v]
		+ LED SCREENx1 [3-D] [3v]
		+ WATER PUMPx2 [4-5:D] [5v]
		+ MOISTUREx2 [0-1:A] [3v]
		+
*/

// Define pins
#define LED_PIN_A           1
#define LED_PIN_B           2
#define LED_SCREEN_PIN      3
#define WATER_PUMP_PIN_A    4
#define WATER_PUMP_PIN_B    5
#define LIGHT_SENS_PIN_A    A0
#define LIGHT_SENS_PIN_B    A1
#define MOISTURE_PIN_A      A2
#define MOISTURE_PIN_B      A3

#define LED_RING_PIXELS     12
#define LED_COLOR[]         {204, 51, 255}

// Hardware objects
Adafruit_NeoPixel ledRingA(LED_RING_PIXELS, LED_PIN_A, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel ledRingB(LED_RING_PIXELS, LED_PIN_B, NEO_GRB + NEO_KHZ800);

LiquidCrystal_I2C lcd(0x3f, 16, 2);

// water pump
// moisture
// light sens

// publics
bool ledA_mode = false;
bool ledB_mode = false;


void setup() {

	pinMode(LED, OUTPUT); // Declare the LED as an output

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

	//water pump

	//moisture

	Serial.begin(115200);
}


void TurnLEDRing(bool mode, String type) {
	if (type == "A")
	{
		for (int i = 0; i < LED_RING_PIXELS; i++) {

			pixels.setPixelColor(i, ledRingA.Color(LED_COLOR[0], LED_COLOR[1], LED_COLOR[2]));
			pixels.show();
		}
	}
	else if (type == "B")
	{
		for (int i = 0; i < LED_RING_PIXELS; i++) {

			pixels.setPixelColor(i, ledRingB.Color(LED_COLOR[0], LED_COLOR[1], LED_COLOR[2]));
			pixels.show();
		}
	}
}

void WriteToLCD(String text){
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

void TurnPump(int dur, String type) {
	//
}

void int GetMoisture(String type) {
	//
	return 0;
}

void int GetLightSensor(String type) {
	//
	return 1;
}


void loop() {

  if (Serial.available() > 0){
    //delay(100);
    String msg = Serial.readStringUntil('\n');
    //WriteToLCD(msg, 0);

    if (msg.substring(0, 5) == "#LCD#")
    {
		// #LCD#message
        WriteToLCD(msg.substring(5));
        Serial.print("Done LCD");
    }
    else if (msg.substring(0, 11) == "#T_LEDRING#")
    {
		//#T_LEDRING#0/1;A/B
		String m = msg.substring(11);
		if (m[0] == '0')
			TurnLEDRing(true, m.substring(2))
		else if (m[0] == '1')
			TurnLEDRing(false, m.substring(2))
    }
	else if (msg.substring(0, 8) == "#T_PUMP#")
	{
		//#T_PUMP#10/[time];A/B
		String m = msg.substring(8);
		TurnPump((int)(m[0]+m[1]), m.substring(2))
	}
    else if (msg.substring(0, 9) == "#MOISTURE#")
    {
		//#GET_MOISTURE#A/B
        String m = msg.substring(9);
        int mois = GetMoisture(m)
        Serial.print("#MOISTURE#" + m.ToString());
    }
	else if (msg.substring(0, 7) == "#LIGHT#")
	{
		//#GET_LIGHT#A/B
		String m = msg.substring(7);
		int mois = GetLightSensor(m)
		Serial.print("#LIGHT#" + m.ToString());
	}
    else
    {
        Serial.print("ERROR" + msg);
    }

  }
}
