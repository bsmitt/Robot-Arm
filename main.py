
import time
from machine import Pin, PWM, I2C
import mcp23017
from state_machine import encoderValue


# =========================================================
# I2C SETUP
# =========================================================

# MCP23017: motor direction pins and limit switches
mcpI2C = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
mcp = mcp23017.MCP23017(mcpI2C, 0x20)

# ESP32: Xbox controller data
i2c = I2C(1, sda=Pin(2), scl=Pin(3), freq=100000)
SLAVE_ADDR = 0x55


# =========================================================
# MCP23017 DIRECTION PINS
# =========================================================

baseDir = 0
shoulderDir = 1
elbowDir = 2
wrist_rightDir = 3
wrist_leftDir = 4
gripperDir = 5

for pin in (
    baseDir, shoulderDir, elbowDir,
    wrist_rightDir, wrist_leftDir, gripperDir
):
    mcp.pin(pin, mode=0)


# =========================================================
# LIMIT SWITCH INPUTS
# =========================================================

baseMS = 6
shoulderMS = 7
elbowMS = 8
pitchMS = 9
rollMS = 10
gripperMS = 11

for pin in (
    baseMS, shoulderMS, elbowMS,
    pitchMS, rollMS, gripperMS
):
    mcp.pin(pin, mode=1, pullup=True)
    
baseSwitchPrev = False
shoulderSwitchPrev = False
elbowSwitchPrev = False
pitchSwitchPrev = False
rollSwitchPrev = False
gripperSwitchPrev = False

# =========================================================
# MOTOR PWM OUTPUTS
# =========================================================

basePWM = PWM(Pin(9), freq=1000, duty_u16=0)
shoulderPWM = PWM(Pin(8), freq=1000, duty_u16=0)
elbowPWM = PWM(Pin(7), freq=1000, duty_u16=0)
wrist_rightPWM = PWM(Pin(6), freq=1000, duty_u16=0)
wrist_leftPWM = PWM(Pin(5), freq=1000, duty_u16=0)
gripperPWM = PWM(Pin(4), freq=1000, duty_u16=0)


# =========================================================
# ENCODERS
# =========================================================

baseEncoder = encoderValue(16)
shoulderEncoder = encoderValue(18)
elbowEncoder = encoderValue(20)
wrist_rightEncoder = encoderValue(14)
wrist_leftEncoder = encoderValue(12)
gripperEncoder = encoderValue(10)


# =========================================================
# MOTOR CONTROL FUNCTIONS
# =========================================================



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


def joystickSpeed(value):
    value = min(127, abs(value))
    return int((value / 127) * 65535)


def stopMotors():
    baseRun(0, 0)
    shoulderRun(0, 0)
    elbowRun(0, 0)
    wrist_rightRun(0, 0)
    wrist_leftRun(0, 0)
    gripperRun(0, 0)


# =========================================================
# CONTROL SETTINGS
# =========================================================

DEADZONE = 10

# 0 = Wrist mode
# 1 = X mode
aButtonCount = 1
aButton_prev = False

# Encoder positions
baseCount = 0
shoulderCount = 0
elbowCount = 0
wrist_rightCount = 0
wrist_leftCount = 0
gripperCount = 0



print("Pico motor controller started")
print("Looking for ESP32 at I2C address 0x55")


# =========================================================
# MAIN LOOP
# =========================================================

while True:

    # -----------------------------------------------------
    # UPDATE ENCODERS AND LIMIT SWITCHES
    # -----------------------------------------------------
    #BASE   
    baseLimit = (mcp.pin(baseMS) == 0)
    if baseLimit and not baseSwitchPrev:
        baseEncoder.resetCount()
        baseCount = 0

    # Keep count at zero while switch is pressed
    elif baseLimit:
        baseCount = 0

    else:
        newBaseRaw = baseEncoder.getCount()

        if newBaseRaw is not None:
            baseCount = newBaseRaw

    baseSwitchPrev = baseLimit
 
    #SHOULDER   
    shoulderLimit = (mcp.pin(shoulderMS) == 0)
    if shoulderLimit and not shoulderSwitchPrev:
        shoulderEncoder.resetCount()
        shoulderCount = 0

    # Keep count at zero while switch is pressed
    elif shoulderLimit:
        shoulderCount = 0

    else:
        newShoulderRaw = shoulderEncoder.getCount()

        if newShoulderRaw is not None:
            shoulderCount = newShoulderRaw

    shoulderSwitchPrev = shoulderLimit
    
    # -----------------------------------------------------
    # READ SIX BYTES FROM THE ESP32
    # -----------------------------------------------------

    try:
        data = i2c.readfrom(SLAVE_ADDR, 8)

    except OSError:
        stopMotors()
        print("ESP32 I2C read failed")
        time.sleep_ms(100)
        continue

    # Byte layout:
    # 0 = switches/buttons
    # 1 = reset/stick-click buttons
    # 2 = left stick X
    # 3 = left stick Y
    # 4 = right stick X
    # 5 = right stick Y
    # 6 = left trigger
    # 7 = right trigger

    RxByte0 = data[0]
    RxByte1 = data[1]

    joystickX = data[2]
    joystickY = data[3]
    joystickX2 = data[4]
    joystickY2 = data[5]
    
    leftTrig = data[6]
    rightTrig = data[7]

    # Buttons
    joy1 = bool(RxByte1 & 0x01)
    joy2 = bool(RxByte1 & 0x02)

    shareButton = bool(RxByte0 & 0x01)
    menuButton = bool(RxByte0 & 0x02)
    rightBump = bool(RxByte0 & 0x04)
    leftBump = bool(RxByte0 & 0x08)
    aButton = bool(RxByte0 & 0x10)
    bButton = bool(RxByte0 & 0x20)
    xButton = bool(RxByte0 & 0x40)
    yButton = bool(RxByte0 & 0x80)

    # -----------------------------------------------------
    # CENTER THE JOYSTICK VALUES
    # -----------------------------------------------------

    x_centered = joystickX - 127
    y_centered = joystickY - 127

    x2_centered = joystickX2 - 127
    y2_centered = joystickY2 - 127

    # Apply deadzone
    if abs(x_centered) <= DEADZONE:
        x_centered = 0

    if abs(y_centered) <= DEADZONE:
        y_centered = 0

    if abs(x2_centered) <= DEADZONE:
        x2_centered = 0

    if abs(y2_centered) <= DEADZONE:
        y2_centered = 0

    # -----------------------------------------------------
    # TOGGLE X MODE / WRIST MODE
    # -----------------------------------------------------

    if aButton and not aButton_prev:
        aButtonCount = (aButtonCount + 1) % 2

        if aButtonCount:
            print("X-MODE")
        else:
            print("WRIST-MODE")

    aButton_prev = aButton


    # -----------------------------------------------------
    # LEFT STICK: BASE/SHOULDER OR WRISTS
    # -----------------------------------------------------

    if aButtonCount:
        # X mode: control base and shoulder
        wrist_rightRun(0, 0)
        wrist_leftRun(0, 0)

        if x_centered > 0:
            baseRun(0, joystickSpeed(x_centered))
        elif x_centered < 0:
            baseRun(1, joystickSpeed(x_centered))
        else:
            baseRun(0, 0)

        if y_centered > 0:

        # Prevent movement toward pressed limit switch
            if shoulderLimit:
                shoulderRun(0, 0)
            else:
                shoulderRun(0, joystickSpeed(y_centered))

        elif y_centered < 0:

            # Always allow movement away from the switch
            shoulderRun(1, joystickSpeed(y_centered))

        else:
            shoulderRun(0, 0)


    else:
        # Wrist mode: stop base and shoulder
        baseRun(0, 0)
        shoulderRun(0, 0)

        # Mix pitch and roll to control two wrist motors
        pitch = x_centered
        roll = y_centered

        right_cmd = max(-127, min(127, pitch + roll))
        left_cmd = max(-127, min(127, pitch - roll))

        # Right wrist
        if right_cmd > 0:
            wrist_rightRun(0, joystickSpeed(right_cmd))
        elif right_cmd < 0:
            wrist_rightRun(1, joystickSpeed(right_cmd))
        else:
            wrist_rightRun(0, 0)

        # Left wrist
        if left_cmd > 0:
            wrist_leftRun(0, joystickSpeed(left_cmd))
        elif left_cmd < 0:
            wrist_leftRun(1, joystickSpeed(left_cmd))
        else:
            wrist_leftRun(0, 0)
        


    # -----------------------------------------------------
    # RIGHT STICK: ELBOW
    # -----------------------------------------------------


    if y2_centered > 0:
        elbowRun(1, joystickSpeed(y2_centered))
    elif y2_centered < 0:
        elbowRun(0, joystickSpeed(y2_centered))
    else:
        elbowRun(0, 0)

    # -----------------------------------------------------
    # TRIGGERS: GRIPPER
    # -----------------------------------------------------

    triggerDeadzone = 10
    
    # Right trigger: CLOSE gripper
    if rightTrig > triggerDeadzone:
        speed = int((rightTrig / 255) * 65535)
        gripperRun(1, speed)

    # Left trigger: OPEN gripper
    elif leftTrig > triggerDeadzone:
        speed = int((leftTrig / 255) * 65535)
        gripperRun(0, speed)

    # Neither trigger pressed: STOP gripper
    else:
        gripperRun(0, 0)

