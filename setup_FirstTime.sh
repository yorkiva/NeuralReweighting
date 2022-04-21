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
    elif [[ $file == "LHAPDF"*".tar.gz" ]]; then
	echo "LHAPDF tar file directory found"
	export NEURWT_LHAPDFTAR=$NEURWT_BASE_PATH/$file
    elif [[ $file == "LHAPDF"* ]]; then
	echo "LHAPDF directory directory found"
	export NEURWT_LHAPDFSRC=$NEURWT_BASE_PATH/$file
    elif [[ $file == "lhapdf" ]]; then
	echo "lhapdf install directory directory found"
	export NEURWT_LHAPDFLOC=$NEURWT_BASE_PATH/$file
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

if [[ -z $NEURWT_LHAPDFLOC ]]; then
    echo "No LHAPDF install directory is found!"
    if [[ -z $NEURWT_LHASRC ]]; then
	echo "No LHAPDF source directory is found! Downloading LHAPDF-6.4.0!"
	rm $NEURWT_BASE_PATH/MG*tar.gz
	wget https://lhapdf.hepforge.org/downloads/?f=LHAPDF-6.4.0.tar.gz -O LHAPDF-6.4.0.tar.gz
	export NEURWT_LHAPDFTAR=$NEURWT_BASE_PATH/LHAPDF-6.4.0.tar.gz
	tar -xzf LHAPDF-6.4.0.tar.gz
	export NEURWT_LHAPDFSRC=$NEURWT_BASE_PATH/LHAPDF-6.4.0
	mkdir lhapdf
	export NEURWT_LHAPDFLOC=$NEURWT_BASE_PATH/lhapdf
    fi
    cd $NEURWT_LHAPDFSRC
    ./configure --prefix=$NEURWT_LHAPDFLOC
    make
    make install
    cd -
    export PATH=$PATH:$NEURWT_LHAPDFLOC/bin
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$NEURWT_LHAPDFLOC/lib
    LHAPDF_PYTHON_PATH=`ls -d $NEURWT_LHAPDFLOC/lib/python*`
    if [[ -z LHAPDF_PYTHON_PATH ]]; then
	echo "LHAPDF Python Path not found!"
    else
	if [[ -z $PYTHONPATH ]]; then
	    export PYTHONPATH=$LHAPDF_PYTHON_PATH
	else
	    export PYTHONPATH=$PYTHONPATH:$LHAPDF_PYTHON_PATH
	fi
    fi
    unset LHAPDF_PYTHON_PATH
fi  
# ## Downloading and getting the correct UFO models

# Models=`cat models_to_get.txt`
# unset IFS
# for model in ${Models[*]}
# do
#     echo "Downloading " $model
#     wget $model
#     export IFS='/'
#     read -a strarr <<< "$model"
#     modelname=${strarr[-1]}
#     #echo "cd $NEURWT_MGLOC/models/"
#     #echo $modelname
#     cd "$NEURWT_MGLOC/models/" && tar -xzvf "$NEURWT_BASE_PATH/$modelname" && cd -
#     unset IFS
# done

# unset Models
# unset model
# unset modelname
