
#include <math.h>      
#include "pin_map.h"
#include <PID_v1.h>
#include <AccelStepper.h>

Thermistor Thermistor1(TEMP_0_PIN);
float Temp;
String digits;
String input = "";

// Definir los motores
AccelStepper motor1(AccelStepper::DRIVER, 54, 55); // Motor 1: pin STEP=2, pin DIR=3
AccelStepper motor2(AccelStepper::DRIVER, 26, 28); // Motor 2: pin STEP=4, pin DIR=5
const int enablePin1 = 38; // Pin de habilitación para motor 1
const int enablePin2 = 24; // Pin de habilitación para motor 2
bool motor1Enabled = false;
bool motor2Enabled = false;

// AJUSTES PID
double Setpoint, Input, Output;
double Kp = 22.85, Ki = 1.85, Kd = 70.65;
PID myPID(&Input, &Output, &Setpoint, Kp, Ki, Kd, DIRECT);

void setup(){
  Serial.begin(115200);  
  pinMode(TEMP_0_PIN, INPUT_PULLUP); // configure RAPMS TEMP_0_PIN for reading thermistor. This is MEGA pin 13 from pin_map.h
  pinMode(RAMPS_D9_PIN, OUTPUT);
  pinMode(TEMP_OUT, OUTPUT);
  pinMode(enablePin1, OUTPUT); // Pines de habilitación como salida de motores
  pinMode(enablePin2, OUTPUT); // Pines de habilitación como salida de motores
 
  digitalWrite(enablePin1, LOW); // LOW habilita el A4988
  digitalWrite(enablePin2, LOW); // LOW habilita el A4988

  motor1.setMaxSpeed(5000); // Velocidad máxima para motor 1
  motor1.setAcceleration(100); // Aceleración para motor 1

  motor2.setMaxSpeed(2000); // Velocidad máxima para motor 2
  motor2.setAcceleration(1000); // Aceleración para motor 2

  motor1.move(1000000); // Mover motor 1 a la posición 1000
  motor2.moveTo(100000); // Mover motor 2 a la posición 1000

  Setpoint = 190;  // Temperatura deseada en grados Celsius
  myPID.SetMode(AUTOMATIC); // Iniciar el PID
  myPID.SetOutputLimits(0, 255);  // Salida del PID entre 0 y 255 para PWM
  
}

void loop() {
  delay(10);
  Input = Thermistor1.getValue();        // Leer el Termistor
  Serial.print("TEMP:");
  Serial.print(Input);
  Serial.println("#");
  myPID.Compute(); // Actualizar el PID  // Iniciar el PID
  if (Serial.available()) {
    input = Serial.readStringUntil('\n'); // Leer el Puerto Serial
    if (input.startsWith("ACTUATE:")){
      digits = input.substring(8); // Configurar digits
    }
  }

// ==================================================
// --- MOTOR SPOOL ---
if (digits[0] == '1') {
int motor1Speed = 500;
  if (!motor1Enabled){
   digitalWrite(enablePin1, LOW); // Habilitar el motor 1
   motor1Enabled = true;
   motor1.setSpeed(motor1Speed);
   }
  } else {
   if (motor1Enabled) {
    digitalWrite(enablePin1, HIGH); // Deshabilitar el motor 1
    motor1Enabled = false;
    }
  }
if (motor1Enabled){
    motor1.runSpeed();
  }

// ==================================================
// --- FAN ---
  if(digits[1] == '1'){
      analogWrite(RAMPS_D9_PIN, 150);
  }
  else {
      analogWrite(RAMPS_D9_PIN, 0);
  }
  
// ==================================================
// --- EXTRUDER ---
int motor2Speed = 2000;
if (digits[2] == '1') {
  if (!motor2Enabled){
   digitalWrite(enablePin2, LOW); // Habilitar el motor 2
   motor2Speed = -2000;
   motor2Enabled = true;
   motor2.setSpeed(motor2Speed);
   }
} else { 
  if (motor2Enabled) {
   digitalWrite(enablePin2, HIGH); // Deshabilitar el motor 2
   motor2Enabled = false;
  }
}
if (motor2Enabled){
    motor2.runSpeed();
}

// ==================================================
// --- HEATER ---
// ==================================================
  if(digits[3] == '1' and Input < Setpoint){
    analogWrite(RAMPS_D10_PIN, Output);}
  else{
    analogWrite(RAMPS_D10_PIN, 0);
  }
}
  
