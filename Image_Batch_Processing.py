from PIL import Image
from os import listdir
from os.path import isfile, join
import zipfile
import os
from pathlib import Path
import shutil
from configparser import ConfigParser
import subprocess
from shutil import move
import time

# pyinstaller --add-data "config.ini;." --add-data "ffmpeg.exe;." --add-data "pngquant.exe;." --clean -y Image_Batch_Processing.py

# READ CONFIG INI
config = ConfigParser()
config.read('./config.ini')

path = config.get('section_a', 'input_path')
extracted_files_directory = config.get('section_a', 'output_path')
min_file_size = int(config.get('section_a', 'min_file_size'))
resize_factor = float(config.get('section_a', 'resize_factor'))
compression = int(config.get('section_a', 'compression'))
width = int(config.get('section_a', 'width'))
height = int(config.get('section_a', 'height'))
#max_colors = config.getboolean('section_a', 'max_colors')
jpg_resize = config.getboolean('section_a', 'jpg_resize')
png_resize = config.getboolean('section_a', 'png_resize')
gif_resize = config.getboolean('section_a', 'gif_resize')
convert_av = config.getboolean('section_a', 'convert_av')
video_bitrate = config.get('section_a', 'video_bitrate')
audio_bitrate = config.get('section_a', 'audio_bitrate')
png_quality = config.get('section_a', 'png_quality')
max_png_size = int(config.get('section_a', 'max_png_size'))
process_png = config.getboolean('section_a', 'process_png')
process_jpg = config.getboolean('section_a', 'process_jpg')
process_gif = config.getboolean('section_a', 'process_gif')

def extractScorm(zip_file, extension):
    # btn_select.config(state="disabled")
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        filename = os.path.basename(zip_file)
        dirname = os.path.dirname(zip_file)
        #extract_path = os.path.join(dirname, extracted_files_directory, filename)
        extract_path = os.path.join(extracted_files_directory, filename)
        if extension == "zip":
            extracted_scorm_path = extract_path[:-4]
        else:
            extracted_scorm_path = extract_path[:-6]
        zip_ref.extractall(extracted_scorm_path)
        return extracted_scorm_path

def adjustImage(file_path, image_type, report):
    img = Image.open(file_path) #.convert('RGB')
    global width, height
    png_file_size = os.path.getsize(file_path)
    if png_file_size > min_file_size and img.size[0] >width and img.size[1] > height:
        #print("Original Image Size: " + str(img.size))
        if image_type == 'png':
            report.write("PNG;" + str(img.size).replace(', ', 'x') + ';')

            # REDUCE COLORS
            """global max_colors
            if img.getcolors(maxcolors=256) == None and max_colors == True:
                print("Change color palette to 256!")
                img = img.convert("P", palette=Image.ADAPTIVE, colors=256)

            #print("PNG old size: " + str(os.path.getsize(file_path)))
            report.write(str(os.path.getsize(file_path)) + ';')
            img.save(file_path, optimize=True, quality=compression)
            #print("PNG new file size: " + str(os.path.getsize(file_path)))
            #print("PNG new resolution: " + str(img.size))
            report.write(str(os.path.getsize(file_path)) + ';')
            report.write(str(img.size).replace(', ', 'x') + ';' + '\n') """

            report.write(str(os.path.getsize(file_path)) + ';')

            try:
                subprocess.call('pngquant --quality=' + png_quality + ' --speed 10 --ext _save.png --force ' + file_path, shell=True)
                move(file_path[:-4] + '_save.png', file_path)
            except:
                print("PNG image could not be compressed due to quality reasons!")

            # REDUCE RESOLUTION
            new_file_size = os.path.getsize(file_path)
            if png_resize and new_file_size > max_png_size * 1000:
                try:
                    print("Resizing next image:")
                    img = Image.open(file_path)
                    base = resize_factor # e.g. 1 = original size, 0.5 = half size
                    hsize = int((float(img.size[1] * base)))
                    vsize = int((float(img.size[0] * base)))
                    img = img.resize((vsize, hsize), Image.ANTIALIAS)
                    img.save(file_path, optimize=True)
                    new_file_size = os.path.getsize(file_path)
                except:
                    print("PNG could not be resized!")
                    report.write('\n')
            report.write(str(new_file_size) + ';')
            report.write(str(img.size).replace(', ', 'x'))
        if image_type == 'jpg':
            report.write("JPG;" + str(img.size).replace(', ', 'x') + ';')
            global jpg_resize
            if jpg_resize == True:
                base = resize_factor # e.g. 1 = original size, 0.5 = half size
                hsize = int((float(img.size[1] * base)))
                vsize = int((float(img.size[0] * base)))
                img = img.resize((vsize, hsize), Image.ANTIALIAS)
            #print("JPG old size: " + str(os.path.getsize(file_path)))
            report.write(str(os.path.getsize(file_path)) + ';')
            img.save(file_path, optimize=True, quality=compression)
            #print("JPG new file size: " + str(os.path.getsize(file_path)))
            #print("New resolution: " + str(img.size))
            report.write(str(os.path.getsize(file_path)) + ';')
            report.write(str(img.size).replace(', ', 'x') + '\n')

        elif image_type == 'gif':
            report.write("GIF;" + str(img.size).replace(', ', 'x') + ';')
            global gif_resize
            if gif_resize == True:
                base = resize_factor # e.g. 1 = original size, 0.5 = half size
                hsize = int((float(img.size[1] * base)))
                vsize = int((float(img.size[0] * base)))
                img = img.resize((vsize, hsize), Image.ANTIALIAS)
            #print("GIF old size: " + str(os.path.getsize(file_path)))
            report.write(str(os.path.getsize(file_path)) + ';')
            img.save(file_path, optimize=True, quality=compression)
            #print("GIF new file size: " + str(os.path.getsize(file_path)))
            #print("New resolution: " + str(img.size))
            report.write(str(os.path.getsize(file_path)) + ';')
            report.write(str(img.size).replace(', ', 'x') + '\n')
        else:
            report.write('\n')
    else:
        report.write('This file was skipped due to resize settings;\n')

def adjustAudioVideo(file_path, file_type, report):
    start_time = time.time()
    if file_type == 'mp4':
        report.write('mp4; ;')
        report.write(str(os.path.getsize(file_path)) + ';')
        video = subprocess.run('ffmpeg.exe -i %s -b %s %s -y' % (file_path, video_bitrate, file_path + '_new.mp4'))
        os.remove(file_path)
        os.rename(file_path + '_new.mp4', file_path)
        #video_libx264 = subprocess.run('ffmpeg -i %s -vcodec libx264 -b %s %s -y' % (file_path, video_bitrate, file_path))
        report.write(str(os.path.getsize(file_path)) + '\n')
    elif file_type == 'mp3':
        report.write('mp3; ;')
        report.write(str(os.path.getsize(file_path)) + ';')
        audio = subprocess.run('ffmpeg -i %s -map 0:a:0 -b:a %s %s' % (file_path, audio_bitrate, file_path + '_new.mp3'))
        os.remove(file_path)
        os.rename(file_path + '_new.mp3', file_path)
        report.write(str(os.path.getsize(file_path)) + '\n')
    # SCALE: -s 720x480
    # SCALE based on input size (make it half)
    # ffmpeg -i input.avi -vf scale="iw/2:ih/2" output.avi
    print("--- Video converting time %s ---" % (time.time() - start_time))

def checkImages(extracted_path, report):
    for root, directories, files in os.walk(extracted_path):
        for file in files:
            if (file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.JPG') or file.endswith('.JPEG')) and process_jpg:
                # Create the full filepath
                file_path = os.path.join(root, file)
                print(file_path)
                report.write(file_path + ';')
                adjustImage(file_path, "jpg", report)
            if (file.endswith('.png') or file.endswith('.PNG')) and process_png:
                # Create the full filepath
                file_path = os.path.join(root, file)
                print(file_path)
                report.write(file_path + ';')
                adjustImage(file_path, "png", report)
            if (file.endswith('.gif') or file.endswith('.GIF')) and process_gif:
                # Create the full filepath
                file_path = os.path.join(root, file)
                report.write(file_path + ';')
                print(file_path)
                adjustImage(file_path, "gif", report)
            if file.endswith('.mp4'):
                if convert_av:
                    # Create the full filepath
                    file_path = os.path.join(root, file)
                    print(file_path)
                    report.write(file_path + ';')
                    adjustAudioVideo(file_path, "mp4", report)
                else:
                    print("VIDEO DETECTED: " + str(file_path))
                    report.write('WARNING, VIDEO FILE FOUND (mp4). File size;' + str(os.path.getsize(file_path)) + '\n')
            if file.endswith('.mp3'):
                if convert_av:
                    # Create the full filepath
                    file_path = os.path.join(root, file)
                    print(file_path)
                    report.write(file_path + ';')
                    adjustAudioVideo(file_path, "mp3", report)
                else:
                    print("Audio DETECTED: " + str(file_path))
                    report.write('WARNING, AUDIO FILE FOUND (mp3). File size;' + str(os.path.getsize(file_path)) + '\n')
            if file.endswith('.avi') or file.endswith('.mkv') or file.endswith('.mov') or file.endswith('.wmv'):
                file_path = os.path.join(root, file)
                report.write(file_path + ';')
                print("VIDEO DETECTED: " + str(file_path))
                report.write('WARNING, VIDEO FILE FOUND (not mp4!). File size;' + str(os.path.getsize(file_path)) + '\n')

def zipNewPackage(dir_name, extension):
    print("Creating new SCORM package in directory " + str(Path(dir_name)))
    print("Compressing files, please wait...")
    current_cwd = os.getcwd()
    os.chdir(Path(dir_name).parent)
    try:
        if extension == "zip":
            shutil.make_archive(os.path.basename(dir_name), "zip", Path(dir_name))
            print("cleanup...")
            # delete unzipped files and directory
            shutil.rmtree(dir_name)
        elif extension == "story":
            shutil.make_archive(os.path.basename(dir_name), "zip", Path(dir_name))
            pre, ext = os.path.splitext(dir_name + ".zip")
            try:
                if os.path.exists(dir_name + ".story"):
                    os.remove(dir_name + ".story")
                    print(f"Existing file deleted: {dir_name + '.story'}")
                os.rename(dir_name + ".zip", pre + ".story")
            except:
                print("Error renaming .zip in .story")
            print("cleanup...")
            # delete unzipped files and directory
            shutil.rmtree(dir_name)
    except:
        print(f"Error building package - {os.path.basename(dir_name)}")
    os.chdir(current_cwd)

def compressPackages(path, report):
    for root, dirs, files in os.walk(path):
        for file in files:
            filedir = os.path.join(root, file)
            print(filedir)
            if file.endswith('.zip'):
                #file_path = path + str(file)
                extracted_path = extractScorm(filedir, "zip")
                checkImages(extracted_path, report)
                zipNewPackage(extracted_path, "zip")
            elif file.endswith('.story'):
                extracted_path = extractScorm(filedir, "story")
                checkImages(extracted_path, report)
                zipNewPackage(extracted_path, "story")


    """    all_scorm_files = [f for f in listdir(path) if isfile(join(path, f))]
        for file in all_scorm_files:
            print(file)
            if file.endswith('.zip'):
                file_path = path + str(file)
                extracted_path = extractScorm(file_path)
                checkImages(extracted_path, report)
                zipNewScorm(extracted_path)"""

if __name__ == '__main__':
    try:
        os.makedirs(extracted_files_directory)
    except:
        print('Export directory is present.')
    try:
        report_path = extracted_files_directory + '\\' + 'report.csv'
        report = open(report_path, "w")
        report.write('drive; file path;file type;original resolution;original file size;new file size;new resolution;\n')
        compressPackages(path, report)
        report.close()
    except:
        print("WARNING: report.csv is in use! Please close file and try again.")


