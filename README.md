[#](#) Open Hands Food Pantry Garden Irrigation System

This is a 2017 as an Oakland University Senior Design project to provide the
Open Hands Food Pantry with an autonomous off-grid irrigation system.


# Setup Instructions
```
python -m myenv .myenv  #create python virtual environment
source .myenv/bin/activate #activate the virtual environment
pip install -r requirements.txt #installs dependencies
```

# Running
Either
```
source .myenv/bin/activate
./Interface_Final.py
```
or
```
.myenv/bin/python Interface_Final.py
```

# Install on Arduino
1. Install platformio on Pi
2. `pio run -t upload` -- make sure serial monitor is closed otherwise, this will fail.

# Run App on Boot
1. Put `irrigation.service` into `/etc/systemd/system/`
2. Apply the changes by running
    ```
    sudo systemctl daemon-reload
    sudo systemctl enable irrigation.service
    ```
3. Run `sudo reboot` to test if app auto launches on boot