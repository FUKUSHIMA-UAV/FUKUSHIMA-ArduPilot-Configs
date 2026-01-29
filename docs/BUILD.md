# Build Guide for FUKUSHIMA Flight Controllers

Complete guide to building ArduPilot firmware for FUKUSHIMA F7/H7 flight controllers.

## Prerequisites

### Required Tools
- Ubuntu 20.04+ (or WSL2)
- Git
- Python 3.6+
- ARM GCC toolchain

### ArduPilot Setup
```bash
# Clone ArduPilot
git clone --recurse-submodules https://github.com/ArduPilot/ardupilot.git
cd ardupilot

# Install dependencies
Tools/environment_install/install-prereqs-ubuntu.sh -y
```

## Install FUKUSHIMA Configurations
```bash
# Clone FUKUSHIMA configs
cd ~
git clone https://github.com/FUKUSHIMA-UAV/FUKUSHIMA-ArduPilot-Configs.git

# Copy to ArduPilot
cp -r FUKUSHIMA-ArduPilot-Configs/FUKUSHIMA_H7 \
    ardupilot/libraries/AP_HAL_ChibiOS/hwdef/
cp -r FUKUSHIMA-ArduPilot-Configs/FUKUSHIMA_F7 \
    ardupilot/libraries/AP_HAL_ChibiOS/hwdef/
cp -r FUKUSHIMA-ArduPilot-Configs/FUKUSHIMA_F7-Agri \
    ardupilot/libraries/AP_HAL_ChibiOS/hwdef/
```

## Build Firmware

### FUKUSHIMA_H7
```bash
cd ~/ardupilot
./waf configure --board FUKUSHIMA_H7
./waf copter
```

Output: `build/FUKUSHIMA_H7/bin/arducopter.apj`

### FUKUSHIMA_F7
```bash
./waf configure --board FUKUSHIMA_F7
./waf copter
```

### FUKUSHIMA_F7-Agri
```bash
./waf configure --board FUKUSHIMA_F7-Agri
./waf copter
```

## Build Success

You should see:
```
BUILD SUMMARY
Target          Text (B)  Data (B)  BSS (B)  Total Flash Used (B)  Free Flash (B)
-------------------------------------------------------------------------------------
bin/arducopter   1590724      4556   138256               1595280          370788
'copter' finished successfully (7m4.192s)
```

## Firmware Files

After successful build:
- `.apj` file: For Mission Planner/QGroundControl
- `.abin` file: For bootloader
- `.bin` file: Raw binary

Location: `build/FUKUSHIMA_XX/bin/`

## Build for Different Vehicles
```bash
# Plane
./waf plane

# Rover
./waf rover

# Heli
./waf heli
```

## Troubleshooting

### "Board FUKUSHIMA_H7 not found"
Ensure hwdef files are in correct location:
```bash
ls ardupilot/libraries/AP_HAL_ChibiOS/hwdef/FUKUSHIMA_H7/
```

### Compilation errors
```bash
# Clean and rebuild
./waf clean
./waf configure --board FUKUSHIMA_H7
./waf copter
```

### Out of memory
Reduce build parallelism:
```bash
./waf -j1 copter
```

## Next Steps

- Flash firmware: [FLASHING.md](FLASHING.md)
- Test with SITL: [SITL.md](SITL.md)
- Parameter tuning: [TUNING.md](TUNING.md)

