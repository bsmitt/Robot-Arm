import time
from machine import Pin
import rp2

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
        self.dirPin = Pin(firstPin, Pin.IN, Pin.PULL_UP)
        self.pulsePin = Pin(firstPin + 1, Pin.IN, Pin.PULL_UP)
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
