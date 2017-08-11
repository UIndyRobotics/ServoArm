/*************************************************** 

 ****************************************************/

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// called this way, it uses the default address 0x40
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();


// Depending on your servo make, the pulse width min and max may vary, you 
// want these to be as small/large as possible without hitting the hard stop
// for max range. You'll have to tweak them as necessary to match the servos you
// have!
#define SERVOMIN  150 // this is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX  550 //600 // this is the 'maximum' pulse length count (out of 4096)

#define NUMSERVOS 6

uint16_t last[NUMSERVOS];
int debug_count = 0;


void setup() {
  Serial.setTimeout(100);
  Serial.begin(9600);
  Serial.print("Arm Driver - 's#valu' Values from ");
  Serial.print(SERVOMIN);
  Serial.print(" -> ");
  Serial.println(SERVOMAX);

  pwm.begin();
  
  pwm.setPWMFreq(60);  // Analog servos run at ~60 Hz updates
  // According to http://www.electronicoscaldas.com/datasheet/MG996R_Tower-Pro.pdf the PWM period is 50Hz
  // The above SERVOMIN and SERVOMAX are tied to this frequency!


  yield();
}


void getData(){
  byte syn;
  int got = 0;
  got = Serial.readBytes(&syn,1);
  if(syn != 's' || got == 0){
    /*Serial.print("Junk: ");
    Serial.print(debug_count);
    Serial.print("  ");
    Serial.println(syn[0]);
    debug_count++; */
    return;
  }
  // 6 servos, 3 digits each
  byte data[NUMSERVOS * 3];
  // First byte is servo number, 0-9, 0-9, 0-9.  Really is 155-600
  got = Serial.readBytes(data, NUMSERVOS * 3);
  if(got == 0){
    //Serial.print("got 0");
    return;
  }
  
  for(int i = 0; i < NUMSERVOS * 3; i++){
    if(data[i] < '0' || data[i] > '9'){
      //Serial.println(" Error!");
      return;
    }
  } 
  for(int servo = 0; servo < NUMSERVOS; servo++){
    uint16_t value = data[servo * 3 + 2] - '0';
    value = value + 10 * (data[servo * 3 + 1] - '0');
    value = value + 100 * (data[servo * 3 + 0] - '0');
    

    
    /*Serial.print("Servo: ");
    Serial.print(servo);
    Serial.print(" Amt: " ); */
     
    if(value < SERVOMIN)value = SERVOMIN;
    if(value > SERVOMAX)value = SERVOMAX;
    if(value != last[servo]){
      pwm.setPWM(servo, 2, value);
      last[servo] = value;
      /*Serial.print("Servo: ");
      Serial.print(servo);
      Serial.print(" Amt: " );
      Serial.println(value);*/
    }
    
  }
  //Serial.print("Debug count ");
  //Serial.println(debug_count);
  //debug_count++;
  

}

void loop() {
  getData();
  delay(1);

}
