#include <DHT.h>
#define DHTPIN D5
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

#define SENSOR_PIN D7     // Arduino pin connected to sound sensor's pin

int moisture_pin = A0;

const long eventTime_1_DHTPIN = 1000;
const long eventTime_2_SENSOR_PIN= 5000;
const long eventTime_3_moisture_pin= 1000;
const long eventTime_4_SENSOR_PIN= 5000;


unsigned long previousTime_1 = 0;
unsigned long previousTime_2 = 0;
unsigned long previousTime_3 = 0;
unsigned long previousTime_4 = 0;


int lastSoundState;     // the previous state of sound sensor
int currentSoundState;  // the current state of sound sensor

int sensor_data;

int ledPin = D6;                // choose the pin for the LED
int motionPin = D1;               // choose the input pin (for PIR sensor)
int pirState = LOW;             // we start, assuming no motion detected
int val = 0;                    // variable for reading the pin status

#include <Arduino.h>
#if defined(ESP32)
  #include <WiFi.h>
#elif defined(ESP8266)
  #include <ESP8266WiFi.h>
#endif
#include <Firebase_ESP_Client.h>

//Provide the token generation process info.
#include "addons/TokenHelper.h"
//Provide the RTDB payload printing info and other helper functions.
#include "addons/RTDBHelper.h"

// Insert your network credentials
#define WIFI_SSID "matthew"
#define WIFI_PASSWORD "123456789"

// Insert Firebase project API Key
#define API_KEY "AIzaSyAsHGVndFgrNGQ97v2teg_DzMXL2HFCVzs"

// Insert RTDB URLefine the RTDB URL */
#define DATABASE_URL "bantaybaby-ee224-default-rtdb.firebaseio.com/" 

//Define Firebase Data object
FirebaseData fbdo;

FirebaseAuth auth;
FirebaseConfig config;

//unsigned long sendDataPrevMillis = 0;
//int count = 0;
bool signupOK = false;


void setup() {
  Serial.begin(9600);          // initialize serial
  dht.begin(); // FOR DHT11
  pinMode(SENSOR_PIN, INPUT);  // set arduino pin to input mode
  pinMode(moisture_pin, INPUT);

  pinMode(ledPin, OUTPUT);      // declare LED as output
  pinMode(motionPin, INPUT);     // declare sensor as input

  currentSoundState = digitalRead(SENSOR_PIN);

    // WIFI ONLY
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED){
    Serial.print(".");
    delay(300);
  }
  Serial.println();
  Serial.print("Connected with IP: ");
  Serial.println(WiFi.localIP());
  Serial.println();

    /* Assign the api key (required) */
  config.api_key = API_KEY;

  /* Assign the RTDB URL (required) */
  config.database_url = DATABASE_URL;

  /* Sign up */
  if (Firebase.signUp(&config, &auth, "", "")){
    Serial.println("ok");
    signupOK = true;
  }
  else{
    Serial.printf("%s\n", config.signer.signupError.message.c_str());
  }

  /* Assign the callback function for the long running token generation task */
  config.token_status_callback = tokenStatusCallback; //see addons/TokenHelper.h
  
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);
}

void loop() {
  unsigned long currentTime = millis();

  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  lastSoundState = currentSoundState;           // save the last state
  currentSoundState = digitalRead(SENSOR_PIN);  // read new state



 if (Firebase.ready() && signupOK ) {
  
  if(currentTime - previousTime_2 >= eventTime_2_SENSOR_PIN){
    if(currentSoundState == HIGH && lastSoundState == LOW){
      if(Firebase.RTDB.setInt(&fbdo, "SENSORS/sound", currentSoundState)){
        Serial.println("The sound has been detected");
        previousTime_2 = currentTime; 
      }
      else{
        Serial.println("FAILED");
        Serial.println("REASON: " + fbdo.errorReason());
      }
    }
  }

  if(currentTime - previousTime_4 >= eventTime_4_SENSOR_PIN){
    if (Firebase.RTDB.setInt(&fbdo, "SENSORS/sound", 0)){
      Serial.println("The sound has been 0");
      previousTime_4 = currentTime;
    }
    else{
        Serial.println("FAILED");
        Serial.println("REASON: " + fbdo.errorReason());
    }
  }


  if(currentTime - previousTime_1 >= eventTime_1_DHTPIN){
    if(Firebase.RTDB.setFloat(&fbdo, "SENSORS/humidity",humidity) && Firebase.RTDB.setFloat(&fbdo, "SENSORS/temperature", temperature)){
    Serial.print("Humidity: ");
    Serial.print(humidity);
    Serial.print("% - Temperature: ");
    Serial.print(temperature);
    Serial.println("°C");
    previousTime_1 = currentTime; 
    }
  else{
      Serial.println("FAILED");
      Serial.println("REASON: " + fbdo.errorReason());
    }
  }
  
  sensor_data = analogRead(moisture_pin);
  if (currentTime - previousTime_3 >= eventTime_3_moisture_pin){
    if(Firebase.RTDB.setInt(&fbdo, "SENSORS/moisture",sensor_data)){

      if (sensor_data < 100){
        Serial.println("WET");
      }
      else{
        Serial.println("DRY");
      }
        previousTime_3 = currentTime; 
      }
  else{
    Serial.println("FAILED");
    Serial.println("REASON: " + fbdo.errorReason());
    }
  }


  val = digitalRead(motionPin);  // read input value
  if (Firebase.RTDB.setInt(&fbdo,"SENSORS/motion", val)){
      if (val == HIGH)	// check if the input is HIGH
  {            
    digitalWrite(ledPin, HIGH);  // turn LED ON
	
    if (pirState == LOW) 
	{
      Serial.println("Motion detected!");	// print on output change
      pirState = HIGH;
    }
  } 
  else 
  {
    digitalWrite(ledPin, LOW); // turn LED OFF
	
    if (pirState == HIGH)
	{
      Serial.println("Motion ended!");	// print on output change
      pirState = LOW;
  }
  }
  }
 }
}