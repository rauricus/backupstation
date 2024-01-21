Notes
=====

Installed raspberry pi OS 64-bit Lite (Dec 2023)

- Made a fork from the original repo from Make Magazine
	https://github.com/rauricus/backupstation.git

- Install Git Credential Manager (GCM) on macOS
	
	brew install --cask git-credential-manager

	In order to git push & Co, password authentication no longer works.
	When git push-ing & Co, GCM will open an allow to log in.

---

- Update all installed packages
	sudo apt update
	apt list --upgradable
	sudo apt full-upgrade

- Install pip
	(on debian/ubuntu and derivatives)
	sudo apt install python3-venv python3-pip

	(see https://packaging.python.org/en/latest/guides/installing-using-linux-tools/#installing-pip-setuptools-wheel-with-linux-package-managers)


- Install wiringpi package
	pip install wiringpi

- LED wiren und so ein- und ausschalten
	python src/backup-py/greenLEDon.py 
	python src/backup-py/greenLEDoff.py 

---

Kippschalter
------------

- GPIO2 ist als Input konfiguriert. Er misst also die Spannung, die dort anliegt.

- Schalter zum On/Off Schalten eines Ports werden über Pull-up (Default ist on) bzw Pull-down (Default ist off) angebunden. Dies geschieht über eine Schaltung, bei der der Strom entweder über den einen Widerstand oder den Widerstand mit dem Schalter fliesst.
  (see Schalter Basics: https://raspi.tv/2013/how-to-use-wiringpi2-for-python-on-the-raspberry-pi-in-raspbian)

- Der Widerstand _ohne Schalter_ ist ein sog. Pull-up (wenn er den Port "on" schaltet) oder ein Pull-Down (wenn er den Port "off" schaltet) Widerstand.

- Der Raspberry Pi hat _eingebaute_ Pull-up bzw. Pull-down Widerstände, die per Software aktiviert werden können.
  Dadurch muss nur noch ein Schalter angeschlossen werden, der entweder auf 3.3V (wenn pull-down aktiviert) oder auf GND (wenn pull-up aktiviert) führt, wenn er geschlossen ist
  (see Schalter mit eingebauten Pull-up/Pull-down Widerständen: https://raspi.tv/2013/how-to-use-wiringpi2-for-python-with-pull-ups-or-pull-downs-and-pwm)


  