import sys, signal
#https://doc.qt.io/qtforpython-6/PySide6/QtBluetooth/QBluetoothDeviceDiscoveryAgent.html#PySide6.QtBluetooth.QBluetoothDeviceDiscoveryAgent.setLowEnergyDiscoveryTimeout
from PyQt5.QtBluetooth import QBluetoothDeviceDiscoveryAgent, QBluetoothDeviceInfo, QBluetoothLocalDevice
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSlot as Slot, pyqtSignal as Signal

doDebug = True
def myprint(*items, doPrint=False):
	if doDebug or doPrint:
		print(*items)

def deviceType(device):
	theType = device.coreConfigurations()
	if theType == QBluetoothDeviceInfo.UnknownCoreConfiguration:
		return "The type of the Bluetooth device cannot be determined."
	elif theType == QBluetoothDeviceInfo.BaseRateCoreConfiguration:
		return "The device is a standard Bluetooth device."
	elif theType == QBluetoothDeviceInfo.BaseRateAndLowEnergyCoreConfiguration:
		return "The device is a Bluetooth Smart device with support for standard and Low Energy device."
	elif theType == QBluetoothDeviceInfo.LowEnergyCoreConfiguration:
		return "The device is a Bluetooth Low Energy device."
	else:
		return "Tool outdated: Unknown device type."

class btAgent(QObject):
	def deviceDiscovered(self, device):
		deviceID = device.address().toString()
		if (deviceID in self.targetIDs) and (device not in self.found):
			self.found.append(device)
			myprint("device!!!", device.name(), deviceID)
			if len(self.targetIDs) == len(self.found):
				self.agent.stop()
				myprint("all required devices discovered, stopping discovery")
				if doDebug:
					print(">>>HERE IS SOME INFO ABOUT THE FOUND DEVICES<<<")
					for device_i in self.found:
						print(f" > ID=({device_i.address().toString()}), NAME=({device_i.name()}), TYPE=({deviceType(device_i)}), SIGNALSTRENGTH=({device_i.rssi()})")
				self.pairall()

	def pairall(self):
		myprint("trying to pair all devices...")
		for device_i in self.found:
			self.local.requestPairing(device_i.address(), QBluetoothLocalDevice.AuthorizedPaired)

	def discoveryFinished(self):
		myprint("discovery done:", self.agent.discoveredDevices())
		if len(self.targetIDs) != len(self.found):
			myprint("could not discover all required devices, exiting...")
			sys.exit(1)

	def errorOccurred(self, error):
		myprint(f"ERROR ({type(error)}) occured!", error, doPrint=True)
		sys.exit(2)

	def pairingFinished(self, address, pairingStatus):
		if pairingStatus == QBluetoothLocalDevice.Unpaired:
			myprint("Could not pair requested device!", address, pairingStatus)
		else:
			myprint("Successfully paired: ", address)

	def __init__(self, parent=None):
		super().__init__(parent)
		self.targetIDs = ["98:B0:8B:CC:A0:09", ]
		self.found = []
		self.agent = QBluetoothDeviceDiscoveryAgent(self)
		self.agent.setLowEnergyDiscoveryTimeout(30000)
		self.local = QBluetoothLocalDevice(self)
		myprint(f"local hostMode={self.local.hostMode()} (0=HostPoweredOff, 1=HostConnectable, 2=HostDiscoverable, 3=HostDiscoverableLimitedInquiry)")
		if self.local.hostMode() == QBluetoothLocalDevice.HostPoweredOff:
			print("Bluetooth is off, exiting...")
		# connects
		self.agent.deviceDiscovered.connect(self.deviceDiscovered)
		self.agent.finished.connect(self.discoveryFinished)
		self.agent.error.connect(self.errorOccurred)
		self.local.pairingFinished.connect(self.pairingFinished)
		self.local.error.connect(self.errorOccurred)
		myprint(f"Going to scan for devices for {self.agent.lowEnergyDiscoveryTimeout()/1000} seconds...")
		self.agent.start() # TODO: filter for BLE devices

app = QApplication(sys.argv)
signal.signal(signal.SIGINT, signal.SIG_DFL)

test = btAgent()

sys.exit(app.exec())
print("Bye bye :-)")
