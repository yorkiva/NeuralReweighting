#!/bin/bash

unset NEURWT_MGTAR
unset NEURWT_MGLOC
unset NEURWT_BASE_PATH
unset NEURWT_LHAPDFLOC
unset NEURWT_LHAPDFTAR
unset NEURWT_LHAPDFSRC
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
    elif [[ $file == "LHAPDF"*"tar.gz" ]]; then
	 echo "LHAPDF tar file found"
	 export NEURWT_LHAPDFTAR=$NEURWT_BASE_PATH/$file
    elif [[ $file == "LHAPDF"* ]]; then
	 echo "LHAPDF source loc found"
	 export NEURWT_LHAPDFSRC=$NEURWT_BASE_PATH/$file
    elif [[ $file == "lhapdf" ]]; then
	 echo "LHAPDF install loc found"
	 export NEURWT_LHAPDFLOC=$NEURWT_BASE_PATH/$file
	 export PATH=$PATH:$NEURWT_LHAPDFLOC/bin
	 export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$NEURWT_LHAPDFLOC/lib
	 LHAPDF_PYTHON_PATH=`ls -d $NEURWT_LHAPDFLOC/lib/python*`
	 if [[ -z LHAPDF_PYTHON_PATH ]]; then
	     echo "LHAPDF Python Path not found!"
	     exit 1
	 else
	     export PYTHONPATH=$PYTHONPATH:$LHAPDF_PYTHON_PATH
	 fi
	 unset LHAPDF_PYTHON_PATH
    fi
done

if [[ -z $NEURWT_MGLOC ]]; then ## MG is not there!
    echo "No MG is found! Please Run the script 'setup_FirstTime.sh' before starting!"
    exit 1
elif [[ -z $NEURWT_LHAPDFLOC ]]; then ## LHAPDF is not there!
    echo "No LHAPDF is found! Please Run the script 'setup_FirstTime.sh' before starting!"
    exit 1
else
    echo "Setup Successful!"
fi

 
