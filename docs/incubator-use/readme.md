# Installation and use
The perfusion drive modules can be installed and used in compatible cell culture incubators that have an access port in the back side. The plug for translating the cable and connector while preventing leakage in this repository is compatible with ports 31mm in diameter and 45-50mm in length. To accommodate different port dimensions, the cable plug [step file]() can be modified.

### Required materials:
[**Mechanical assembly and control box**](/dynamic-cell-culture-drive/blob/main/docs/assembly/README.md)
**Cable plug:**
- 2x 3D printed cable plug model
- 1x o-ring 2x26mm FPM 70
- 1x o-ring 2x28mm FPM 70
- 4x M3, 10mm screw
- 4x M3 hexagonal nut
**Control box - motor connection:**
connectors: [WEIPU SF1210 / P7II](https://www.weipuconnector.com/products/push-pull-sf12/?creative=747527646460&keyword=&matchtype=&network=g&device=c&gad_campaignid=16004278745)
motor cable: [LiY-CY; 8x0.34mm2](https://www.tme.eu/en/details/liycy-8x0.34/multicore-cables-shielded/lapp/0034508/)

### Installation:
1. assemble 1 Liy-CY motor cable with 2 WEIPU connectors, one on each side
2. assemble the cable plug by encasing two printed models around the cable, fastening with o-rings and securing with M3 screws/nuts
3. Install the cable-connector-plug into the incubator port so connecting and disconnecting the perfusion module is performed in the direction that secures port stability.
4. Cover the connector inside the incubator with the protective cap
5. Sterilize the cable and connector by wiping with 70% Ethanol and let residual Ethanol evaporate

### Usage:
1. Surface disinfect the perfusion module by spraying and wiping with 70% Ethanol and leave to dry in a laminar flow hood.
2. When starting an experiment, place the perfusion module inside the cell culture incubator and connect to electronics control box.
3. Set-up [liquid handling components](/dynamic-cell-culture-drive/tree/main/liquid%20handling)
4. Start experiment
5. After the experiment is completed (maximum duration 30 days), disconnect perfusion module and protect connector with cap. Disinfect perfusion module and leave to dry.
