#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>

#define DHTPIN 2
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

// Set the LCD address to 0x27 for a 16 chars and 2 line display (could also be 0x3F depending on your module)
// SDA connects to A4, SCL connects to A5 on Arduino Uno
LiquidCrystal_I2C lcd(0x27, 16, 2);

String candidateName = "BYIRINGIRO ALOYS "; // Length > 16 to enable scrolling
int scrollPosition = 0;
unsigned long previousScrollMillis = 0;
const long scrollInterval = 800; // milliseconds per scroll step (increased to make it slower)

unsigned long prevTempMillis = 0;
const long tempInterval = 2000; // Read temperature every 2 seconds

float currentTemp = 0.0;

void setup() {
  Serial.begin(9600);
  
  // Initialize LCD
  lcd.init();
  lcd.backlight();
  
  // Initialize DHT sensor
  dht.begin();
  
  // Initial display setup
  lcd.setCursor(0, 1);
  lcd.print("Temp: -- C      ");
}

void loop() {
  unsigned long currentMillis = millis();
  
  // --- Temperature Reading and Serial output ---
  if (currentMillis - prevTempMillis >= tempInterval) {
    prevTempMillis = currentMillis;
    
    // Read temperature as Celsius
    float t = dht.readTemperature();
    
    // Check if any reads failed and exit early (to try again)
    if (isnan(t)) {
      Serial.println("Error reading DHT sensor");
    } else {
      currentTemp = t;
      
      // Send data to PC via Serial in a parseable format
      Serial.print("TEMP:");
      Serial.println(currentTemp);
      
      // Update second row on LCD
      lcd.setCursor(0, 1);
      lcd.print("Temp: ");
      lcd.print(currentTemp);
      lcd.print(" C  "); // Spaces to clear any trailing characters
    }
  }
  
  // --- Scrolling first row ---
  if (currentMillis - previousScrollMillis >= scrollInterval) {
    previousScrollMillis = currentMillis;
    
    lcd.setCursor(0, 0);
    
    if (candidateName.length() > 16) {
      // Wrap-around scrolling logic
      String toPrint = "";
      int len = candidateName.length();
      for (int i = 0; i < 16; i++) {
        toPrint += candidateName.charAt((scrollPosition + i) % len);
      }
      lcd.print(toPrint);
      
      scrollPosition++;
      if (scrollPosition >= len) {
        scrollPosition = 0;
      }
    } else {
      lcd.print(candidateName);
      // Pad with spaces if less than 16 to clear row
      for(int i = candidateName.length(); i < 16; i++) {
        lcd.print(" ");
      }
    }
  }
}
