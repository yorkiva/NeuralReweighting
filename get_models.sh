#!/bin/bash

## Downloading and getting the correct UFO models

if [[ -z $1 ]]; then
    Models=`cat models_to_get.txt`
else
    Models=$1
fi

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
