from machine import Pin, ADC  
import time
from machine import UART
import didplay_font as font
from machine import Pin, SPI
import st7789

BACKLIGHT_PIN = 16
RESET_PIN = 15
DC_PIN = 7
CS_PIN = 6
CLK_PIN = 5
DIN_PIN = 4 
CHG = ADC(Pin(19))
CHG.atten(ADC.ATTN_11DB)
ps2_y = ADC(Pin(18))
ps2_y.atten(ADC.ATTN_11DB)
ps2_x = ADC(Pin(17))
ps2_x.atten(ADC.ATTN_11DB)
uart=UART(2,9600,rx=48,tx=45) 
CHG_ps = CHG.read()


spi = SPI(1, baudrate=31250000, sck=Pin(CLK_PIN), mosi=Pin(DIN_PIN))
tft = st7789.ST7789(spi, 240, 320,
    reset=Pin(RESET_PIN, Pin.OUT),
    cs=Pin(CS_PIN, Pin.OUT),
    dc=Pin(DC_PIN, Pin.OUT),
    backlight=Pin(BACKLIGHT_PIN, Pin.OUT),
    rotation=3)
tft.init()
old_y = 0
old_x = 0
rs = 0
T = 0
H = 0
while True:
    CHG_ps = CHG.read()
    if CHG_ps < 200:
        l = 5
        r = 1
    else:
        l = 4
        r = 2
    val_y = ps2_y.read()
    val_x = ps2_x.read()
    #Direction
    if val_y >= 1900 and val_y <= 2150:
        val_y = 3
        disp_y = "None"
    elif val_y > 2100 and val_y <= 3000:
        val_y = r#2
        disp_y = "<-  "
    elif val_y > 3000:
        val_y = r#1
        disp_y = "<---"
    elif val_y < 1900 and val_y >= 1000:
        val_y = l#4
        disp_y = "->  "
    elif val_y < 1000:
        val_y = l#5 
        disp_y = "--->"
    # Speed
    if val_x >= 1900 and val_x <= 2200:
        val_x = 3
    elif val_x > 2200 and val_x <= 3200:
        val_x = 2
    elif val_x > 3200:
        val_x = 1
    elif val_x < 1900 and val_x >= 1000:
        val_x = 4
    elif val_x < 1000:
        val_x = 5
    
    if val_y != old_y or val_x != old_x:
        #send = 'BEG,'+str(val_y) + ',' + str(val_x)+',END'
        send = 'A'+str(int(val_y) + int(val_x)*10)+'B'
        uart.write(send)#.encode('ascii'))
        #print("Send")
        #print(send)
        time.sleep(0.1)
        old_y = val_y
        old_x = val_x
        pr = "X:"+str(val_x)
        tft.text(font,pr, 10, 0, st7789.color565(255,255,255), st7789.color565(0,0,0))
        pr = "Y:"+str(val_y)
        tft.text(font,pr, 10, 50, st7789.color565(255,255,255), st7789.color565(0,0,0))
    if uart.any():
        rs = uart.read(7)
        rs = rs.decode('utf-8')#接收128个字符
        print(rs)
        rs = list(rs)
        if rs[0] == 'T' and rs[6] == 'F':
            rs.pop(0)
            rs.pop()
            T = rs[0]+rs[1]
            H = rs[3]+rs[4]
        val_y = ps2_y.read()
        val_x = ps2_x.read()
    #Direction
        
        if val_y >= 1900 and val_y <= 2150:
             val_y = 3
             disp_y = "None"
        elif val_y > 2100 and val_y <= 3000:
             val_y = r#2
             disp_y = "<-  "
        elif val_y > 3000:
             val_y = r#1
             disp_y = "<---"
        elif val_y < 1900 and val_y >= 1000:
             val_y = l#4
             disp_y = "->  "
        elif val_y < 1000:
             val_y = l#5
             disp_y = "--->"
    # Speed
        if val_x >= 1900 and val_x <= 2200:
             val_x = 3
        elif val_x > 2200 and val_x <= 3200:
             val_x = 2
        elif val_x > 3200:
             val_x = 1
        elif val_x < 1900 and val_x >= 1000:
             val_x = 4
        elif val_x < 1000:
             val_x = 5
        
        send = 'A'+str(int(val_y) + int(val_x)*10)+'B'
        uart.write(send)#.encode('ascii'))
        uart.write(send)#.encode('ascii'))
        uart.write(send)#.encode('ascii'))
        pr = "X:"+str(val_x)
        tft.text(font,pr, 10, 0, st7789.color565(255,255,255), st7789.color565(0,0,0))
        pr = "Y:"+str(val_y)
        tft.text(font,pr, 10, 50, st7789.color565(255,255,255), st7789.color565(0,0,0))
        
    pr = "Temp:"+ str(T)
    tft.text(font,pr, 10, 100, st7789.color565(255,255,255), st7789.color565(0,0,0))
    pr = "H:"+ str(H)
    tft.text(font,pr, 10, 150, st7789.color565(255,255,255), st7789.color565(0,0,0))
    pr ="CHG:"+str(CHG_ps)
    tft.text(font,pr, 10, 200, st7789.color565(255,255,255), st7789.color565(0,0,0))