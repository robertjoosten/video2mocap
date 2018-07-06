@echo off

set ZIP_EXE=7z\7za.exe
set WGET_EXE=wget\wget.exe

:: Download ZIP
echo ----- Downloading OpenPose -----
set ZIP_NAME=openpose-1.3.0-win64-gpu-binaries.zip
%WGET_EXE% -c https://github.com/CMU-Perceptual-Computing-Lab/openpose/releases/download/v1.3.0/%ZIP_NAME% -P /
echo:

echo ----- Unzipping OpenPose -----
%ZIP_EXE% x %ZIP_NAME%
echo:

echo ----- Deleting Temporary Zip File %ZIP_NAME% -----
del "%ZIP_NAME%"

echo ----- Renaming Directory to be version agnostic -----
rename openpose-1.3.0-win64-gpu-binaries openpose

echo ----- OpenPose Models Downloaded -----
cd openpose/models
call getModels.bat

echo ----- OpenPose ( + Models ) Downloaded and Unzipped -----