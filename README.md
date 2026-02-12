# Modular perfusion and motion drive for dynamic cell culture experiments

This repository contains the documentation for building and using a modular flow set-up designed to support multiple modes of dynamic cell culture. It is operable inside standard cell culture incubators (37°C, 5% CO<sub>2</sub>, high humidity) without affecting internal conditions (e.g., temperature increase, contaminant formation) and is compatible with standard cell culture workflows. The described system allows three modes of perfusion or nutrient exchange for 3D cell culture models:
1.	Peristaltic pumping
  - standard method in laboratory and industrial environments,
  - enables controlled medium exchange and shear force generation,
  - suitable for adherent cultures on flat substrates and within tissue scaffolds.
2.	Wave-based rocking (wave bioreactor principle)
  - provides gentle perfusion through oscillating liquid flow in a closed system,
  - suitable for suspension cultures and tissue scaffold cultures.
3.	Rotating chamber culture
  - closed system with continuous rotation and even nutrient consumption,
  - suitable for suspension cultures and microcarrier-based cultures.

## Assembly and user documentation

The documentation files for this project is listed below. You can find them in the
**[Docs](./docs/)** folder.

- **[Installation Guide](docs/INSTALLATION.md)** - How to install and start the backend and frontend
  services.
- **[Assembly Guide](docs/assembly/README.md)** - Mechanical assembly of the project.
- **[Hardware Setup Guide](docs/setup/README.md)** - Hardware setup for system configuration
  services.
- **[Backend System Information](docs/backend/README.md)** - Information on backend system
  functionalities.
- **[Frontend System Information](docs/frontend/README.md)** - Information on frontend system
  functionalities.
- **[User Guide](docs/user_guide/README.md)** - User Guide on service functionalities.
- **[Liquid Handling Use Cases](liquid%20handling)** - Use cases for liquid handling using the different modules.
- **[Updating Services](docs/services_update/README.md)** - Information on how to update services.


![Figure1](https://github.com/Institute-of-Biomedical-Sciences/dynamic-cell-culture-drive/blob/main/graphics/hardware-photo.jpg)

Figure: Manufactured motion drive modules, from left to right: rocking platform, electronics box, peristaltic pump drive, rotary drive.


### Authors
[Boštjan Vihar](mailto:bostjan.vihar@um.si) <sup>1</sup>
[Jernej Vajda](mailto:jernej.vajda@um.si) <sup>1</sup>
Nejc Klemenčič <sup>2</sup>
Bine Zgaga <sup>2</sup>
Mihael Miško <sup>2</sup>
Jure Zagoranski <sup>2</sup>
Luka Mustafa <sup>2</sup>

1 - Institute of Biomedical Sciences, Faculty of Medicine, University of Maribor, Taborska ulica 8, SI-2000, Maribor
2 - IRNAS Ltd., Limbuška cesta 76b, SI-2000 Maribor


### Acknowledgements
This work is supported by the European Comission through the FEASTS project  (Project ID 101136749, call HORIZON-CL6-2023-FARM2FORK-01-13).

![logos - feasts, EU](graphics/logos.png)

### License

Shield: [![CC BY-SA 4.0][cc-by-sa-shield]][cc-by-sa]

This work is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International
License][cc-by-sa].

[![CC BY-SA 4.0][cc-by-sa-image]][cc-by-sa]

[cc-by-sa]: http://creativecommons.org/licenses/by-sa/4.0/
[cc-by-sa-image]: https://licensebuttons.net/l/by-sa/4.0/88x31.png
[cc-by-sa-shield]: https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg




