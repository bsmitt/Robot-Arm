def baseRun(direction, speed):
    mcp.pin(baseDir, value=direction)
    basePWM.duty_u16(speed)

def shoulderRun(direction, speed):
    mcp.pin(shoulderDir, value=direction)
    shoulderPWM.duty_u16(speed)
    
def elbowRun(direction, speed):
    mcp.pin(elbowDir, value=direction)
    elbowPWM.duty_u16(speed)
    
def wrist_rightRun(direction, speed):
    mcp.pin(wrist_rightDir, value=direction)
    wrist_rightPWM.duty_u16(speed)
    
def wrist_leftRun(direction, speed):
    mcp.pin(wrist_leftDir, value=direction)
    wrist_leftPWM.duty_u16(speed)
    
def gripperRun(direction, speed):
    mcp.pin(gripperDir, value=direction)
    gripperPWM.duty_u16(speed)
    


mcpI2C = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1))
mcp = mcp23017.MCP23017(mcpI2C, 0x20)

i2c = I2C(1, sda=Pin(2), scl=Pin(3), freq=100_000)
SLAVE_ADDR = 0x55

#Direction Pins (MCP23017)
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

#Microswitches (MCP23017)
baseMS = 6
shoulderMS = 7
elbowMS = 8
pitchMS = 9
rollMS = 10
gripperMS = 11

mcp.pin(baseMS, mode=1, pullup=True)
mcp.pin(shoulderMS, mode=1, pullup=True)
mcp.pin(elbowMS, mode=1, pullup=True)
mcp.pin(pitchMS, mode=1, pullup=True)
mcp.pin(rollMS, mode=1, pullup=True)
mcp.pin(gripperMS, mode=1, pullup=True)

#Encoder state machine assign (Pi Pico)
baseEncoder=encoderValue(16)
shoulderEncoder=encoderValue(18)
elbowEncoder=encoderValue(20)
wrist_rightEncoder=encoderValue(14)
wrist_leftEncoder=encoderValue(12)
gripperEncoder=encoderValue(10)


#PWM Pins (Pi Pico) (max speed 65535)
basePWM = PWM(Pin(9), freq = 1000, duty_u16=0)
shoulderPWM = PWM(Pin(8), freq = 1000, duty_u16=0)
elbowPWM = PWM(Pin(7), freq = 1000, duty_u16=0)
wrist_rightPWM = PWM(Pin(6), freq = 1000, duty_u16=0)
wrist_leftPWM = PWM(Pin(5), freq = 1000, duty_u16=0)
gripperPWM = PWM(Pin(4), freq = 1000, duty_u16=0)
