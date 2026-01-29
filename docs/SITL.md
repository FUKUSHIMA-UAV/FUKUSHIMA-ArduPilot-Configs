# SITL (Software-In-The-Loop) Simulation Guide

Test FUKUSHIMA flight controllers without hardware using ArduPilot's SITL environment.

## Prerequisites

### System Requirements
- Ubuntu 20.04 or later (or WSL2 on Windows)
- 4GB+ RAM
- 10GB+ free disk space

### Install ArduPilot
```bash
# Clone ArduPilot
cd ~
git clone --recurse-submodules https://github.com/ArduPilot/ardupilot.git
cd ardupilot

# Install dependencies
Tools/environment_install/install-prereqs-ubuntu.sh -y

# Setup environment
export PATH=$PATH:$HOME/ardupilot/Tools/autotest
export PATH=/usr/lib/ccache:$PATH
```

## Running SITL

### Basic Simulation
```bash
cd ~/ardupilot
./waf configure --board sitl
./waf copter

# Start SITL with console and map
sim_vehicle.py -v ArduCopter --console --map
```

### Test Flight Commands
```bash
# Check status
status

# View all parameters
param show

# Change flight mode
mode GUIDED

# Arm motors
arm throttle

# Takeoff to 10m
takeoff 10

# Land
land
```

## Testing FUKUSHIMA Configurations

While SITL uses virtual sensors, you can verify parameter configurations:
```bash
# Check IMU settings
param show INS_*

# Check sensor status
sensors

# View GPS data
param show GPS*

# Battery monitoring
param show BATT*
```

## Expected Output

When SITL starts successfully, you should see:
```
Loaded module map
Log Directory: 
Telemetry log: mav.tlog
Waiting for heartbeat from tcp:127.0.0.1:5760
Detected vehicle 1:1 on link 0
STABILIZE> Received 1365 parameters
```

### Sensor Status Example
```
GPS: Fix Type 6, 10 satellites
Battery: 12.6V, 100%
IMU1: Active (ID: 2753028)
IMU2: Active (ID: 2753036)
Barometer: 2 units detected
EKF3: Using GPS
```

## Connecting Mission Planner (Optional)

1. Start SITL as above
2. Open Mission Planner on Windows
3. Connect to: TCP, 127.0.0.1, Port 5760

## Troubleshooting

### "No module named MAVProxy"
```bash
pip install MAVProxy --break-system-packages
```

### "Permission denied"
```bash
chmod +x Tools/autotest/sim_vehicle.py
```

### SITL won't start
```bash
# Clean build
./waf clean
./waf configure --board sitl
./waf copter
```

## Advanced Usage

### Custom Parameters

Load FUKUSHIMA-specific parameters:
```bash
param load /path/to/fukushima_params.parm
```

### Record Flight Data
```bash
# Logs are automatically saved in:
# ~/ardupilot/logs/
```

### Multi-Vehicle Simulation
```bash
sim_vehicle.py -v ArduCopter -I 0
sim_vehicle.py -v ArduCopter -I 1
```

## Next Steps

- Build firmware for actual FUKUSHIMA hardware: [BUILD.md](BUILD.md)
- Flash firmware to board: [FLASHING.md](FLASHING.md)
- Parameter tuning guide: [TUNING.md](TUNING.md)

## Resources

- [ArduPilot SITL Documentation](https://ardupilot.org/dev/docs/sitl-simulator-software-in-the-loop.html)
- [MAVProxy Documentation](https://ardupilot.org/mavproxy/)
- [Mission Planner](https://ardupilot.org/planner/)

