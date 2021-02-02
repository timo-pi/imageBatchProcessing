from PIL import Image
from os import listdir
from os.path import isfile, join
import zipfile
import os
from pathlib import Path
import shutil
from configparser import ConfigParser

# pyinstaller --add-data "config.ini;." --clean -y Image_Batch_Processing.py

# READ CONFIG INI
config = ConfigParser()
config.read('./config.ini')

path = config.get('section_a', 'path')
extracted_files_directory = config.get('section_a', 'extracted_files_directory')
min_file_size = int(config.get('section_a', 'min_file_size'))
resize_factor = float(config.get('section_a', 'resize_factor'))
compression = int(config.get('section_a', 'compression'))
width = int(config.get('section_a', 'width'))
height = int(config.get('section_a', 'height'))
max_colors = bool(config.get('section_a', 'max_colors'))
jpg_resize = bool(config.get('section_a', 'jpg_resize'))
png_resize = bool(config.get('section_a', 'png_resize'))
gif_resize = bool(config.get('section_a', 'gif_resize'))
video_bitrate = config.get('section_a', 'video_bitrate')

def extractScorm(zip_file):
    # btn_select.config(state="disabled")
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        filename = os.path.basename(zip_file)
        dirname = os.path.dirname(zip_file)
        #extract_path = os.path.join(dirname, extracted_files_directory, filename)
        extract_path = os.path.join(extracted_files_directory, filename)
        extracted_scorm_path = extract_path[:-4]
        zip_ref.extractall(extracted_scorm_path)
        return extracted_scorm_path

def adjustImage(file_path, image_type, report):
    img = Image.open(file_path) #.convert('RGB')
    global width, height
    if os.path.getsize(file_path) > min_file_size and img.size[0] >width and img.size[1] > height:
        #print("Original Image Size: " + str(img.size))

        """# GET ALPHA LAYER
        red, green, blue, alpha = img.split()
        print("alpha: " + str(alpha))"""

        # RESIZE IMAGE
        if image_type == 'png':
            report.write("PNG;" + str(img.size).replace(', ', 'x') + ';')
            global png_resize
            if png_resize == True:
                base = resize_factor # e.g. 1 = original size, 0.5 = half size
                hsize = int((float(img.size[1] * base)))
                vsize = int((float(img.size[0] * base)))
                img = img.resize((vsize, hsize), Image.ANTIALIAS)
            # REDUCE COLORS
            global max_colors
            if img.getcolors(maxcolors=256) == None and max_colors == True:
                print("Change color palette to 256!")
                img = img.convert("P", palette=Image.ADAPTIVE, colors=256)

            #print("PNG old size: " + str(os.path.getsize(file_path)))
            report.write(str(os.path.getsize(file_path)) + ';')
            img.save(file_path, optimize=True, quality=compression)
            #print("PNG new file size: " + str(os.path.getsize(file_path)))
            #print("PNG new resolution: " + str(img.size))
            report.write(str(os.path.getsize(file_path)) + ';')
            report.write(str(img.size).replace(', ', 'x') + ';' + '\n')

        elif image_type == 'jpg':
            report.write("JPG;" + str(img.size).replace(', ', 'x') + ';')
            global jpg_resize
            print(jpg_resize)
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
            report.write(str(img.size).replace(', ', 'x') + ';' + '\n')

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
            report.write(str(img.size).replace(', ', 'x') + ';' + '\n')
        else:
            print("File size < 100 Bytes or resolution < 32x32 pixels")

def checkImages(extracted_path, report):
    for root, directories, files in os.walk(extracted_path):
        for file in files:
            if file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.JPG') or file.endswith('.JPEG'):
                # Create the full filepath
                file_path = os.path.join(root, file)
                print(file_path)
                report.write(file_path + ';')
                adjustImage(file_path, "jpg", report)
            if file.endswith('.png') or file.endswith('.PNG'):
                # Create the full filepath
                file_path = os.path.join(root, file)
                print(file_path)
                report.write(file_path + ';')
                adjustImage(file_path, "png", report)
            if file.endswith('.gif') or file.endswith('.GIF'):
                # Create the full filepath
                file_path = os.path.join(root, file)
                report.write(file_path + ';')
                print(file_path)
                adjustImage(file_path, "gif", report)
            if file.endswith('.mp4') or file.endswith('.avi') or file.endswith('.mkv') or file.endswith('.mov') or file.endswith('.wmv'):
                file_path = os.path.join(root, file)
                report.write(file_path + ';')
                print("VIDEO DETECTED: " + str(file_path))
                report.write('WARNING, VIDEO FILE FOUND. File size;' + str(os.path.getsize(file_path)) + '\n')

def zipNewScorm(dir_name):
    print("Creating new SCORM package in directory " + str(Path(dir_name)))
    print("Compressing files, please wait...")
    current_cwd = os.getcwd()
    os.chdir(Path(dir_name).parent)
    shutil.make_archive(os.path.basename(dir_name), 'zip', Path(dir_name))
    os.chdir(current_cwd)

def compressScormPackages(path, report):
    for root, dirs, files in os.walk(path):
        for file in files:
            filedir = os.path.join(root, file)
            print(filedir)
            if file.endswith('.zip'):
                #file_path = path + str(file)
                extracted_path = extractScorm(filedir)
                checkImages(extracted_path, report)
                zipNewScorm(extracted_path)

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
        print('Export directory already exists')

    report_path = extracted_files_directory + '\\' + 'report.csv'
    report = open(report_path, "w")
    report.write('file path;file type;original resolution;original file size;new file size;new resolution;\n')
    compressScormPackages(path, report)
    report.close()

