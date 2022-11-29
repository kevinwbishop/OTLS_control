import hardware.skyra as skyra # uncomment while run

class Laser(object):
    def __init__(self, laser_dict):
        self.rate = laser_dict['rate']
        self.port = laser_dict['port']
        self.names_to_channels = laser_dict['names_to_channels']
        self.max_powers = laser_dict['max_powers']
        self.min_currents = laser_dict['min_currents']
        self.max_currents = laser_dict['max_currents']
        self.zero_current = {'405': 0, '488': 0, '561': 1000, '638': 0}

        self.min_currents_sk_num = {}
        self.max_currents_sk_num = {}
        self.max_powers_sk_num = {}
        for ch in self.names_to_channels:
            self.min_currents_sk_num[self.names_to_channels[ch]] = self.min_currents[ch]
            self.max_currents_sk_num[self.names_to_channels[ch]] = self.max_currents[ch]
            self.max_powers_sk_num[self.names_to_channels[ch]] = self.max_powers[ch]
        print('Laser Initialized!')
        self.skyraLaser = skyra.Skyra(baudrate=self.rate, port=self.port) # uncomment while run
        self.skyraLaser.setMinCurrents(self.min_currents_sk_num) # uncomment while run
        self.skyraLaser.setMaxCurrents(self.max_currents_sk_num) # uncomment while run
        self.skyraLaser.setMaxPowers(self.max_powers_sk_num) # uncomment while run


    def turn_laser_on(self, wavelength, current):
        self.current = current
        self.skyraLaser.setModulationOn(self.names_to_channels[wavelength]) # uncomment while run
        self.skyraLaser.setDigitalModulation(self.names_to_channels[wavelength], 1) # uncomment while run
        self.skyraLaser.setAnalogModulation(self.names_to_channels[wavelength], 0) # uncomment while run
        self.skyraLaser.setModulationLowCurrent(self.names_to_channels[wavelength], self.zero_current[wavelength]) # uncomment while run
        self.skyraLaser.setModulationHighCurrent(self.names_to_channels[wavelength], self.current) # uncomment while run
        self.skyraLaser.turnOn(self.names_to_channels[wavelength]) # uncomment while run
        print(str(wavelength) + " nm laser turned on! Current = " + str(self.current) + " mA!")


    def update(self, wavelength, current):
        self.current = current
        self.skyraLaser.setModulationHighCurrent(self.names_to_channels[wavelength], self.current) # uncomment while run
        self.skyraLaser.turnOn(self.names_to_channels[wavelength]) # uncomment while run
        print("Laser Current updated to " + str(self.current) + " mA")

    def turn_laser_off(self):
        self.skyraLaser.turnOff(self.names_to_channels[self.wavelength]) # uncomment while run
        print(str(self.wavelength) + " nm laser turned off!")