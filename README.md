**WARNING!! Work in Progress**

This is the code repository for Neural Reweighting Project. The dataset is generated by simulating parton level event records from MadGraph with reweighting enabled. Then a DNN is trained to approximate the reweighting factor.

### First Setup

Please fork and checkout the repository from this github [url](https://github.com/yorkiva/NeuralReweighting). If you are using it for the first time, please run the command

```
source setup_FirstTime.sh
```

It will automatically download **MadGraph** version 2.8.3.2 and **LHAPDF** version 6.4.0. It will also download any new physics UFO models necesary. The default UFOs explored in this project have been listed in `models_to_get.txt`. This file contains the `https` download links for each UFO, and obtained with the `wget` command. If you want to add new UFOs, please either add the corresponding link in the `models_to_get.txt` file or download them manually after running the `setupMG.sh` script and place the extracted model directories inside the `$NEURWT_MGLOC/models` directory. The following environment variables will be set by the script:

- `$NEURWT_BASE_PATH`: Absolute path to the project directory
- `$NEURWT_MGLOC`: Absolute path to the location of MadGraph  are set up by the setup script.
- `$NEURWT_LHAPDFLOC`: Absolute path to the location of installed LHAPDF

### Returning Setup

Each time you use return to use the project, run the command

```
source setup.sh
```

This will setup the necessary environment variables necessary for the project.
