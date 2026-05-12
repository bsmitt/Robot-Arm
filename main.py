import time
from machine import Pin, PWM, I2C
import rp2
import mcp23017

class encoderValue:
    counter=0
    @rp2.asm_pio(in_shiftdir=rp2.PIO.SHIFT_RIGHT)
    def pulseCount():
        mov(x, null)
        label('start')
        wait(1, pin, 1)
        wait(0, pin, 1)
        jmp(pin, 'ccw')
        mov(x, invert(x))
        jmp(x_dec, 'inc')
        label('inc')
        mov(x, invert(x))
        mov(isr, x)
        push()
        jmp('start')
        label('ccw')
        jmp(x_dec, 'dec')
        label('dec')
        mov(isr, x)
        push()
        jmp('start')
    
    def __init__(self, firstPin):
        self.dirPin = Pin(firstPin, Pin.IN)
        self.pulsePin = Pin(firstPin + 1, Pin.IN)
        self.sm = rp2.StateMachine(encoderValue.counter, encoderValue.pulseCount, freq=1_000_000, in_base=self.dirPin, jmp_pin=self.dirPin)
        self.sm.active(1)
        
        encoderValue.counter += 1
    
    def getCount(self): #stops bottle necking from non moving encoder
        if self.sm.rx_fifo() > 0:
            raw = self.sm.get()
            if raw > 0x7FFFFFFF:
                return raw - 0x100000000
            return raw
        return None

i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1))
print(i2c.scan())


#mcpI2C = I2C(0, scl=Pin(1), sda=Pin(0), freq=100000)
#print(mcpI2C.scan())

#mcp = mcp23017.MCP23017(mcpI2C, 0x20)

baseEncoder=encoderValue(16)
shoulderEncoder=encoderValue(18)
elbowEncoder=encoderValue(20)
wristrightEncoder=encoderValue(14)
wristleftEncoder=encoderValue(12)
gripperEncoder=encoderValue(10)

basePWM = PWM(Pin(9), freq = 1000, duty_u16=65535)
shoulderPWM = PWM(Pin(8), freq = 1000, duty_u16=65535)
elbowPWM = PWM(Pin(7), freq = 1000, duty_u16=65535)
wristrightPWM = PWM(Pin(6), freq = 1000, duty_u16=65535)
wristleftPWM = PWM(Pin(5), freq = 1000, duty_u16=65535)
gripperPWM = PWM(Pin(4), freq = 1000, duty_u16=65535)


while True:
    baseCount = baseEncoder.getCount()
    shoulderCount = shoulderEncoder.getCount()
    elbowCount = elbowEncoder.getCount()
    wristrightCount = wristrightEncoder.getCount()
    wristleftCount = wristleftEncoder.getCount()
    gripperCount = gripperEncoder.getCount()
    
    basePWM.duty_u16(65535)
    shoulderPWM.duty_u16(0)
    elbowPWM.duty_u16(0)
    wristrightPWM.duty_u16(0)
    wristleftPWM.duty_u16(0)
    gripperPWM.duty_u16(0)
    
    