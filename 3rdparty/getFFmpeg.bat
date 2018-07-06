@echo off

set ZIP_EXE=7z\7za.exe
set WGET_EXE=wget\wget.exe

:: Download FFmpeg
echo ----- Downloading FFmpeg-----
set ZIP_NAME=ffmpeg-20180630-9f0077c-win64-static.zip
%WGET_EXE% -c https://ffmpeg.zeranoe.com/builds/win64/static/%ZIP_NAME% -P /
echo:

echo ----- Unzipping FFmpeg-----
%ZIP_EXE% x %ZIP_NAME%
echo:

::echo ----- Deleting Temporary Zip File %ZIP_NAME% -----
del "%ZIP_NAME%"

echo ----- Renaming Directory to be version agnostic -----
rename ffmpeg-20180630-9f0077c-win64-static ffmpeg

echo ----- FFmpeg Downloaded and Unzipped -----