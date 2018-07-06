import os
import sys
import shutil
import subprocess

from absl import flags
from utils import logging


# ----------------------------------------------------------------------------


# define flags
flags.DEFINE_string("mayapy_exe", "mayapy.exe", "Path to mayapy.exe")
flags.DEFINE_string("python2_exe", "python.exe", "Path to python.exe (2)")
flags.DEFINE_string("python3_exe", "python3.exe", "Path to python.exe (3)")

flags.DEFINE_string("video_path", None, "Path to source video")
flags.DEFINE_string("output_dir", None, "Output dir for characters")
flags.DEFINE_boolean("keep_temp", 0, "Keep temp dir for debugging")


# ----------------------------------------------------------------------------


# static variables
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
APP_DIR = os.path.join(ROOT_DIR, "3rdparty")
FFMPEG_EXE = os.path.join(APP_DIR, "ffmpeg", "bin", "ffmpeg.exe")
HMR_DIR = os.path.join(APP_DIR, "hmr")
OPEN_POSE_DIR = os.path.join(APP_DIR, "openpose")
OPEN_POSE_EXE = os.path.join(OPEN_POSE_DIR, "bin", "OpenPoseDemo.exe")


# ----------------------------------------------------------------------------


def makedirs(path):
    """
    :param str path:
    """
    if not os.path.exists(path):
        os.makedirs(path)


# ----------------------------------------------------------------------------


def video2mocap(
        video_path, 
        output_dir, 
        keep_temp=False,
        mayapy_exe="mayapy.exe", 
        python2_exe="python.exe", 
        python3_exe="python3.exe"
):
    """
    Convert a video to maya scenes containing a animated human ik skeleton.

    Step 1:
        OpenPose is used to get the bounding boxes of the characters in the
        video. This data is stored in a json file generated for each frame.

    Step 2:
        FFmpeg is used to convert the video into individual image files. These
        images are needed for the next step. The images are stored as in a png
        file format.

    Step 3:
        HMR is used to export a json file for each of the frames and the 3D
        matrices that are found in each of the images. The OpenPose json file
        is used to crop the image to only look at a single person at the same
        time.

    Step 4:
        Maya standalone is used to read the json file and generate an animated
        human ik skeleton for each character found.


    :param video_path:
    :param output_dir:
    :param keep_temp:
    :param mayapy_exe:
    :param python2_exe:
    :param python3_exe:
    :return:
    """
    # log settings
    logger.info("---- VIDEO > MOCAP ----")
    logger.info("---- SETTINGS ----")
    logger.info("Video:                 {}".format(video_path))
    logger.info("Output:                {}".format(output_dir))
    logger.info("Keep temp directory:   {}".format(keep_temp))
    logger.info("---- PYTHON ----")
    logger.info("Python 2:              {}".format(python2_exe))
    logger.info("Python 3:              {}".format(python3_exe))
    logger.info("Python Maya:           {}".format(mayapy_exe))    
    
    # create temp dir
    temp_dir = os.path.join(output_dir, "temp")
    
    logger.info("---- TEMP ----")
    logger.info("Directory:             {}".format(temp_dir)) 
    
    makedirs(temp_dir)
     
    # run openpose
    open_pose_json_dir = os.path.join(temp_dir, "openpose_data")
    open_pose_command = [
        OPEN_POSE_EXE,
        "--video", video_path,
        "--write_json", open_pose_json_dir 
    ] 
    
    logger.info("---- OPEN POSE ----")
    logger.info("Command:               {}".format(" ".join(open_pose_command)))
    
    subprocess.check_call(open_pose_command, cwd=OPEN_POSE_DIR)
    
    
    # run ffmpeg
    images_dir = os.path.join(temp_dir, "images_data")
    images_path = os.path.join(images_dir, "image%04d.png")
    ffmpeg_command = [
        FFMPEG_EXE,
        "-i", video_path, images_path
    ]
    
    logger.info("---- FFMPEG ----")
    logger.info("Directory:             {}".format(images_path))
    logger.info("Command:               {}".format(" ".join(ffmpeg_command)))
    
    makedirs(images_dir)
    subprocess.check_call(ffmpeg_command)

    # run hmr
    hrm_json_path = os.path.join(temp_dir, "hmr_data.json")
    hmr_command = [
        python3_exe,
        "-m", "export",
        "--img_dir", images_dir,
        "--json_dir", open_pose_json_dir,
        "--log_dir", output_dir,
        "--output_path", hrm_json_path
    ]

    logger.info("---- HMR ----")
    logger.info("Command:               {}".format(" ".join(hmr_command)))

    subprocess.check_call(hmr_command, cwd=HMR_DIR)
    
    # run mayapy
    maya_command = [
        mayapy_exe,
        "-m", "export_maya",
        "--json_path", hrm_json_path,
        "--output_dir", output_dir,
    ]

    logger.info("---- MAYA ----")
    logger.info("Command:               {}".format(" ".join(maya_command)))

    subprocess.check_call(maya_command, cwd=ROOT_DIR)
    
    # remove temporary files
    if not keep_temp:
        shutil.rmtree(temp_dir)


# ----------------------------------------------------------------------------


if __name__ == '__main__':
    # convert data
    config = flags.FLAGS
    config(sys.argv)

    # get logger
    logger = logging.get_logger(config.output_dir)
    
    # convert
    video2mocap(
        config.video_path,
        config.output_dir,
        config.keep_temp,
        config.mayapy_exe,
        config.python2_exe,
        config.python3_exe,
    )
