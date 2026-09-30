import machine
import ssd1306

# Initialize I2C on your working pins (26 and 27)
i2c = machine.I2C(1, sda=machine.Pin(26), scl=machine.Pin(27), freq=400000)

# Initialize the display with your exact hardware address: 0x3d
display = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3d)

# Clear the screen
display.fill(0)

display.text("BEN HAS THE", 16, 10, 1)
display.text("BEST BLOG SITE", 5, 25, 1)
display.text("EVER", 45, 40, 1)

display.show()
