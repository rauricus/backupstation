Notes
=====

Installed raspberry pi OS 64-bit Lite (Dec 2023)

- Made a fork from the original repo from Make Magazine
	https://github.com/rauricus/backupstation.git

- Install Git Credential Manager (GCM) on macOS
	
	brew install --cask git-credential-manager

	In order to git push & Co, password authentication no longer works.
	When git push-ing & Co, GCM will open a popup allowing to log in.

- On Linux / Raspberry OS:
	- Generate an ssh key
	- Add the ssh key to Github for the repository and under "Settings"
	- Add the ssh key to the ssh-agent, else authentication doesn't work:
			eval "$(ssh-agent -s)"
			ssh-add ~/.ssh/github_ed25519

			(github_ed25519 is the generated ssh key)

			
	Then git pull and also git push works.

---

- Update all installed packages
	sudo apt update
	apt list --upgradable
	sudo apt full-upgrade

- Install pip
	(on debian/ubuntu and derivatives)
	sudo apt install python3-venv python3-pip

	(see https://packaging.python.org/en/latest/guides/installing-using-linux-tools/#installing-pip-setuptools-wheel-with-linux-package-managers)


- Create a Python virtual environment and activate it, install all requirements
	python -m venv .venv
	source .venv/bin/activate
	pip3 install -r requirements.txt

	To install manually:

	- Install wiringpi package
		pip3 install wiringpi

	- Install spidev module
		pip3 install spidev

	- Install RPi module
		pip3 install RPi.GPIO

	- Install PIL module
		pip3 install Pillow

- LED wiren und so ein- und ausschalten
	python src/backup-py/greenLEDon.py 
	python src/backup-py/greenLEDoff.py 

---

- rdiff installieren
	sudo apt-get install rdiff-backup

- store SMB credentials in a special file and protect it (a bit)
	sudo vi /etc/.smb-credentials-theca
	sudo chmod 600 .smb-credentials-theca

  File contains a username, password and an optional workgroup
	username=Andreas
	password=value

	(domain=value) <- did not put that there

- add smb volume to backup to /etc/fstab
	sudo vi /etc/fstab
	
	//theca.heimnetz.localnet/home	/mnt/network/home	cifs	uid=root,file_mode=0777,dir_mode=0777,credentials=/etc/.smb-credentials-theca

- create corresponding folder
	sudo mkdir /mnt/network
	sudo mkdir /mnt/network/home

- format external hd
	sudo fdisk -l

	Shows all disks. The external disk is mentioned there, too (e.g
	Disk /dev/sda: 4.55 TiB, 5000981078016 bytes, 9767541168 sectors)

  ** Note that fdisk can't create any partition larger than 2TB. **

  We there for use parted or gdisk.

  Source: https://www.cyberciti.biz/tips/fdisk-unable-to-create-partition-greater-2tb.html

  1. Check if GPT support is enabled in the kernel. 

  	 If not, Pi won't boot and might corrupt a disk.

  	 sudo modprobe configs
  	 zcat /proc/config.gz | grep "CONFIG_EFI_PARTITION"

  	 Should return "y"

  2. Run parted and create a new partition

  	 sudo parted /dev/sda (if that's the disk)

  	 	mklabel gpt
  	 		creates new partition table
  	 	unit TB
  	 		uses TB as unit to use
  	 	mkpart primary 0 5
  	 		makes a 5TB primary partition
	 		print
	 			shows the current partition table
 			quit
 				saves changes and quits

 	3. Format the partition

 			sudo mkfs.ext4 /dev/sda1

- add external hd to /etc/fstab
	sudo vi /etc/fstab

	/dev/sda1	/mnt/ext_hdd	ext4	rw	0	0

	** Note that, once external hd is there, the Pi will not boot up completely,
	   if the disk is missing during boot. There might be a timeout at one point,
	   but I had to re-connect it to go through the entire startup. **

- create corresponding folder and give it to pi user
	sudo mkdir /mnt/ext_hdd
	sudo chown pi /mnt/ext_hdd

- test if we can mount all drives
	sudo mount -a


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

---

ePaper Display
--------------

- Die Treiberdateien sind dabei. Tritt ein "File not found" Fehler im "init" auf, dann muss das SPI im Raspberry Pi enabled werden.

	- Run sudo raspi-config
	- Select "Interfacing Options"
	- Arrow down to "SPI"
	- Select yes when it asks you to enable SPI
  
 ---

Problems
--------

This error means that a script using the Waveshare EPD doesn't find its device drivers, etc.

(backup.venv) pi@backup-station:~/backupstation $ python3 src/backup-py/backup_ctrl.py 
INFO:root:Starting ePaper display...
INFO:root:... inited
INFO:root:... cleared
INFO:root:cannot open resource

Either change to src/backup-py and run from there. 
I plan to attempt to fix this by switching to the waveshare-epaper module.
	https://pypi.org/project/waveshare-epaper/

