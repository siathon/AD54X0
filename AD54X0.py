# AD5420/AD5410

from machine import Pin, SPI
from micropython import const
from time import sleep_us

TYPE_AD5420 = const(16)
TYPE_AD5410 = const(12)

STATUS_REG  = const(0x00)
DATA_REG    = const(0x01)
CONTROL_REG = const(0x02)

RANGE_4_20 = const(0x05)
RANGE_0_20 = const(0x06)
RANGE_0_24 = const(0x07)

IOUT_FAULT    = const(0x04)
SR_ACTIVE     = const(0x02)
OVRHEAT_FAULT = const(0x01)

SR_CLK_257730 = const(0x00)
SR_CLK_198410 = const(0x01)
SR_CLK_152440 = const(0x02)
SR_CLK_131580 = const(0x03)
SR_CLK_115740 = const(0x04)
SR_CLK_69440  = const(0x05)
SR_CLK_37590  = const(0x06)
SR_CLK_25770  = const(0x07)
SR_CLK_20160  = const(0x08)
SR_CLK_16030  = const(0x09)
SR_CLK_10290  = const(0x0A)
SR_CLK_8280   = const(0x0B)
SR_CLK_6900   = const(0x0C)
SR_CLK_5530   = const(0x0D)
SR_CLK_4240   = const(0x0E)
SR_CLK_3300   = const(0x0F)

SR_STEPSIZE_1   = const(0x00)
SR_STEPSIZE_2   = const(0x20)
SR_STEPSIZE_4   = const(0x40)
SR_STEPSIZE_8   = const(0x60)
SR_STEPSIZE_16  = const(0x80)
SR_STEPSIZE_32  = const(0xA0)
SR_STEPSIZE_64  = const(0xC0)
SR_STEPSIZE_128 = const(0xE0)

CONTROL_REG_ADDR = const(0x55)
DATA_REG_ADDR    = const(0x01)
RESET_REG_ADDR   = const(0x56)

class AD54X0:
    def __init__(self, spi: SPI, latch: Pin, clear: Pin, fault: Pin, tp=TYPE_AD5410):
        self._spi = spi
        self._latch = latch
        self._clear = clear
        self._fault = fault
        self.resolution = tp
        self.fault_handler = None
        
        self._spi.init(polarity=0, phase=0, bits=8)
        self._latch.init(mode=Pin.OUT, value=0)
        self._clear.init(mode=Pin.OUT, value=0)
        self._fault.init(mode=Pin.IN, pull=Pin.PULL_UP)
        self._fault.irq(handler=self._default_fault_handler, trigger=Pin.IRQ_FALLING)
        
    def set_fault_handler(self, handler):
        self.fault_handler = handler
        
    def latch(self):
        self._latch(1)
        sleep_us(10)
        self._latch(0)
        
    def read_register(self, register_addr):
        self._spi.write(bytes([0x02, 0x00, register_addr]))
        self.latch()
        result = self._spi.read(3)
        self.latch()
        return result
        
    def set_config(self,
                   output_range = None,
                   daisy_chain  = None,
                   slew_rate_en = None,
                   slew_step    = None,
                   slew_clock   = None,
                   output_en    = None,
                   ext_resistor = None):
        """
            configure control register
        """
        ctrl_reg = list(self.read_register(CONTROL_REG))
        
        if output_range is not None:
            ctrl_reg[2] &= 0xF8
            ctrl_reg[2] |= output_range
            
        if daisy_chain is not None:
            ctrl_reg[2] &= 0xF7
            ctrl_reg[2] |= daisy_chain << 3
            
        if slew_rate_en is not None:
            ctrl_reg[2] &= 0xEF
            ctrl_reg[2] |= slew_rate_en << 4
            
        if slew_step is not None:
            ctrl_reg[2] &= 0x1F
            ctrl_reg[2] |= slew_step
            
        if slew_clock is not None:
            ctrl_reg[1] &= 0xF0
            ctrl_reg[1] |= slew_clock
            
        if output_en is not None:
            ctrl_reg[1] &= 0xEF
            ctrl_reg[1] |= output_en << 4
            
        if ext_resistor is not None:
            ctrl_reg[1] &= 0xDF
            ctrl_reg[1] |= ext_resistor << 5
        
        ctrl_reg[0] = CONTROL_REG_ADDR
        self._spi.write(bytes(ctrl_reg))
        self.latch()
    
    def set_output_reg(self, data):
        """
            set output register
        """
        buf = bytes([DATA_REG_ADDR, (data & 0xFF00) >> 8, data & 0xFF])
        self._spi.write(buf)
        self.latch()
        
    def set_output_ma(self, data):
        """
            set output to required current(ma)
        """
        rng = list(self.read_register(CONTROL_REG))[2] & 0x7
        if rng == 0x5:
            mx = 20
            mn = 4
        elif rng == 0x6:
            mx = 20
            mn = 0
        else:
            mx = 24
            mn = 0
            
        reg = round((data - mn) * (2 ** self.resolution / (mx - mn)))
        if self.resolution == 12:
            reg = reg << 4
        if reg > 0xFFFF:
            reg = 0xFFFF
        if reg < 0:
            reg = 0
        buf = bytes([DATA_REG_ADDR, (reg & 0xFF00) >> 8, reg & 0xFF])
        self._spi.write(buf)
        self.latch()
        
    def clear(self):
        """
            set output to range minimum
        """
        self._clear(1)
        sleep_us(1)
        self._clear(0)
        
    def reset(self):
        """
            reset device to power-on state
        """
        buf = bytes([RESET_REG_ADDR, 0x00, 0x01])
        self._spi.write(buf)
        self.latch()
        
    def get_status(self):
        """
            get status register
        """
        result = list(self.read_register(STATUS_REG))[0]
        return result
    
    def _default_fault_handler(self, p):
        status_register = self.get_status()
        print(f"AD54X0 fault detected! status register: {status_register:02X}")
        if self.fault_handler:
            self.fault_handler(status_register)