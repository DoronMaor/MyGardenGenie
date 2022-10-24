
#include <Wire.h> 
#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(0x3f, 16, 2);

const int joyX = A0;
const int joyY = A1;


void setup() {
  // LCD Panel
  Wire.begin(); 
  Serial.begin(9600); // open the serial port at 9600 bps:
  lcd.begin(16, 2);
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.setBacklight(HIGH);
  }

void loop() {
  lcd.backlight();
  lcd.setCursor(0,0);
  lcd.print("123123123123");

} // end loop
