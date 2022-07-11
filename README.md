# AD54X0
Micropython library for AD5410/20

simple example for esp32:
```
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
  
  ad.set_config(output_range=RANGE_4_20, output_en=True)
  ad.set_output_ma(9.66)
```
