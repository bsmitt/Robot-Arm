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

mcpI2C = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1))
mcp = mcp23017.MCP23017(mcpI2C, 0x20)



baseDir = 0
shoulderDir = 1
elbowDir = 2
wrist_rightDir = 3
wrist_leftDir = 4
gripperDir = 5

mcp.pin(baseDir, mode=0)
mcp.pin(shoulderDir, mode=0)
mcp.pin(elbowDir, mode=0)
mcp.pin(wrist_rightDir, mode=0)
mcp.pin(wrist_leftDir, mode=0)
mcp.pin(gripperDir, mode=0)

baseEncoder=encoderValue(16)
shoulderEncoder=encoderValue(18)
elbowEncoder=encoderValue(20)
wrist_rightEncoder=encoderValue(14)
wrist_leftEncoder=encoderValue(12)
gripperEncoder=encoderValue(10)

basePWM = PWM(Pin(9), freq = 1000, duty_u16=65535)
shoulderPWM = PWM(Pin(8), freq = 1000, duty_u16=65535)
elbowPWM = PWM(Pin(7), freq = 1000, duty_u16=65535)
wrist_rightPWM = PWM(Pin(6), freq = 1000, duty_u16=65535)
wrist_leftPWM = PWM(Pin(5), freq = 1000, duty_u16=65535)
gripperPWM = PWM(Pin(4), freq = 1000, duty_u16=65535)


while True:
    baseCount = baseEncoder.getCount()
    shoulderCount = shoulderEncoder.getCount()
    elbowCount = elbowEncoder.getCount()
    wrist_rightCount = wrist_rightEncoder.getCount()
    wrist_leftCount = wrist_leftEncoder.getCount()
    gripperCount = gripperEncoder.getCount()
    
    basePWM.duty_u16(0)
    shoulderPWM.duty_u16(0)
    elbowPWM.duty_u16(0)
    wrist_rightPWM.duty_u16(65535)
    wrist_leftPWM.duty_u16(65535)
    gripperPWM.duty_u16(0)
    
    mcp.pin(wrist_leftDir, value=1)
    mcp.pin(wrist_rightDir, value=0)