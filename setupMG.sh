#!/bin/bash

unset NEURWT_MGTAR
unset NEURWT_MGLOC
unset NEURWT_BASE_PATH
export NEURWT_BASE_PATH=`pwd`
ALL_FILES=`ls $NEWRWT_BASE_PATH`

for file in ${ALL_FILES[*]}
do
    if [[ $file == "MG5"*"tar.gz" ]]; then
	echo "MG5 tar file found"
	export NEURWT_MGTAR=$NEURWT_BASE_PATH/$file
    elif [[ $file == "MG5"* ]]; then
	echo "MG5 directory found"
	export NEURWT_MGLOC=$NEURWT_BASE_PATH/$file
    fi
done

if [[ -z $NEURWT_MGLOC ]]; then ## MG is not there!
    echo "No MG is found! Downloading MG5_aMC_v2_8_3_2!"
    rm $NEURWT_BASE_PATH/MG*tar.gz
    wget https://launchpad.net/mg5amcnlo/2.0/2.8.x/+download/MG5_aMC_v2.8.3.2.tar.gz
    export NEURWT_MGTAR=$NEURWT_BASE_PATH/MG5_aMC_v2.8.3.2.tar.gz
    tar -xzf MG5_aMC_v2.8.3.2.tar.gz
    export NEURWT_MGLOC=$NEURWT_BASE_PATH/MG5_aMC_v2_8_3_2
fi     
    
## Downloading and getting the correct UFO models

Models=`cat models_to_get.txt`
unset IFS
for model in ${Models[*]}
do
    echo "Downloading " $model
    wget $model
    export IFS='/'
    read -a strarr <<< "$model"
    modelname=${strarr[-1]}
    #echo "cd $NEURWT_MGLOC/models/"
    #echo $modelname
    cd "$NEURWT_MGLOC/models/" && tar -xzvf "$NEURWT_BASE_PATH/$modelname" && cd -
    unset IFS
done

unset Models
unset model
unset modelname
