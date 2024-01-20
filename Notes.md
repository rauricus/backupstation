Notes
-----

Installed raspberry pi OS 64-bit Lite (Dec 2023)

- Made a fork from the original repo from Make Magazine
	https://github.com/rauricus/backupstation.git

- Install Git Credential Manager (GCM) on macOS
	
	brew install --cask git-credential-manager

	In order to git push & Co, password authentication no longer works.
	When git push-ing & Co, GCM will open an allow to log in.


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

- 