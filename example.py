"""
    AD54X0 Test program for ESP32
    connections:
        MOSI -> 23
        MISO -> 19
        SCLK -> 18

        LATCH -> 5
        FAULT -> 21
        CLEAR -> 22
"""

from machine import Pin, SPI
from AD54X0 import *

spi = SPI(2, baudrate=25000000)

# Choose constructor according to chip type
# AD5410
ad = AD54X0(spi, Pin(5), Pin(22), Pin(21), TYPE_AD5410)
# AD5420
# ad = AD54X0(spi, Pin(5), Pin(22), Pin(21), TYPE_AD5420)

"""
Configure control register
    Available options:
        output_range:
            RANGE_4_20
            RANGE_0_20
            RANGE_0_24

        daisy_chain:
            True
            False

        slew_rate_en:
            True
            False
        
        slew_step:
            SR_STEPSIZE_1
            SR_STEPSIZE_2
            SR_STEPSIZE_4
            SR_STEPSIZE_8
            SR_STEPSIZE_16
            SR_STEPSIZE_32
            SR_STEPSIZE_64
            SR_STEPSIZE_128
        
        slew_clock:
            SR_CLK_257730
            SR_CLK_198410
            SR_CLK_152440
            SR_CLK_131580
            SR_CLK_115740
            SR_CLK_69440
            SR_CLK_37590
            SR_CLK_25770
            SR_CLK_20160
            SR_CLK_16030
            SR_CLK_10290
            SR_CLK_8280
            SR_CLK_6900
            SR_CLK_5530
            SR_CLK_4240
            SR_CLK_3300
        
        output_en:
            True
            False

        ext_resistor:
            True
            False
"""

ad.set_config(output_range=RANGE_4_20, output_en=True)

"""
Fault handler
    fault handler function will be called on fault detection
    the status register will be passed tu fault handler
"""

def fault_handler(status):
    if status & IOUT_FAULT == IOUT_FAULT:
        print("Output current fault")
    if status & OVRHEAT_FAULT == OVRHEAT_FAULT:
        print("Core overheat")

ad.set_fault_handler(fault_handler)


"""
Output control
    set output register directly
    ad.set_output_reg(0x5000)

    set to required current(ma)
    ad.set_output_ma(9.66) 
"""

ad.set_output_ma(9.66)