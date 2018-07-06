@echo off

set ZIP_EXE=7z\7za.exe
set WGET_EXE=wget\wget.exe

echo ----- Clone HMR -----
git clone https://github.com/robertjoosten/hmr.git

echo ----- HMR Models Downloaded -----
set ZIP_NAME=models.tar.gz
%WGET_EXE% -c https://people.eecs.berkeley.edu/~kanazawa/cachedir/hmr/%ZIP_NAME% -P /

echo ----- Unzipping HMR Models -----
%ZIP_EXE% x -tgzip -so %ZIP_NAME% | %ZIP_EXE% x -si -ttar -ohmr
echo:

echo ----- Deleting Temporary Zip File %ZIP_NAME% -----
del "%ZIP_NAME%"

echo ----- Installing requirements -----
python3.exe -m pip install -r hmr/requirements.txt

echo ----- Unzipping HMR Models NPY -----
%ZIP_EXE% x hmr/models/neutral_smpl_with_cocoplus_reg.zip -ohmr/models
echo:

echo ----- HMR ( + Models ) Downloaded and Unzipped -----