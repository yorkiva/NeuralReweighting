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
    echo "No MG is found! Please Run the script 'setupMG.sh' before starting!"
    exit 1
else
    echo "Setup Successful!"
fi

 
