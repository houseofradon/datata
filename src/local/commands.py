from .file import get_file_size
from .file import get_folder_size
from .file import count_files_in_folder
from .file import get_file_hash
from .file import get_file_size
from .file import local_file_exist
from .file import verify_and_create_local_folder_path
from .file import get_files_size_diff
from src.mimes import is_jpg, is_png, is_video, get_file_extension
from src.helpers import get_image_comp_command
import os
import sys
import tempfile

def print_path(settings, local_rel_path):
	full_path = "{}{}".format(settings['local'], local_rel_path)
	print ("        '{}'   ".format(full_path))

def folders_info(settings, local_rel_path):
	full_path = "{}{}".format(settings['local'], local_rel_path)
	folder_size = get_folder_size(full_path)
	num_files = count_files_in_folder(full_path)
	print (" FOLDER '{}'   {} Kbytes   {} items ".format(full_path, folder_size, num_files))

def files_info(settings, local_rel_path):
	full_path = "{}{}".format(settings['local'], local_rel_path)
	file_hash = get_file_hash(full_path)
	file_size = get_file_size(full_path)
	print (" FILE '{}'   {} hash {} Kbytes ".format(full_path, file_hash, file_size))

# To use this command we need to use "images" iterator, we we are sure that local_rel_path is a picture.
def compress_images(settings, local_rel_path):
	local_rel_path_clean = local_rel_path.decode('utf-8').encode('utf-8')
	print ("Compressing '{}' ".format(local_rel_path_clean)),

	original_file = "{}{}".format(settings['local'], local_rel_path_clean)
	compress_file = "{}{}".format(settings['local-dest'], local_rel_path_clean)
	
	# We need to verify that compress_file folder structure exist (may be we need to generate folders)
	verify_and_create_local_folder_path(compress_file)

	# Get the command to execute, if JPG or PNG, or return if no picture
	command = get_image_comp_command(original_file, compress_file)
	if not command:
		print ("--not-image")
		return

	# Execute previous instructions, depending on strategy
	if settings['strategy'] == 'overwrite':
		# We need to remove destination file
		if os.path.isfile(compress_file):
			os.remove(compress_file),
			print ("--prev-compressed-removed"),
	elif settings['strategy'] == 'skip-if-exist':
		# If file exist, finish
		if os.path.isfile(compress_file):
			print ("--file-exist")
			return
	else:
		sys.exit("Strategy  '{}' not found".format(settings['strategy']))

	# Execute command
	os.system(command)

	if (local_file_exist(compress_file)) and (int(get_file_size(compress_file)) > 0) :
		print ("--compressed"),
	else:
		print ("--original-file")
		os.system("cp {} {}".format(original_file, compress_file))
		return
	# Now we show the percentage of reduction
	reduction = get_files_size_diff(original_file, compress_file)
	print ("--reduction {}%".format(reduction))

def tar_files(settings, local_rel_path):
	local_rel_path_clean = local_rel_path.decode('utf-8').encode('utf-8')
	extension = get_file_extension(local_rel_path_clean)
	print ("Compressing '{}' with extension '{}' ".format(local_rel_path_clean, extension)),
	# If file is already compressed (or has no extension) skip it
	if extension in ['bz2', 'zip', '']:
		print ('--file-already-compressed --DONE')
		return

	original_file = "{}{}".format(settings['local'], local_rel_path_clean)
	compress_file = "{}{}".format(settings['local'], "{}.tar.bz2".format(local_rel_path_clean))
	# Execute previous instructions, depending on strategy
	if settings['strategy'] == 'overwrite':
		# We need to remove destination file
		if os.path.isfile(compress_file):
			os.remove(compress_file),
			print ("--prev-compressed-removed"),
	elif settings['strategy'] == 'skip-if-exist':
		# If file exist, finish
		if os.path.isfile(compress_file):
			print ("--compressed-file-exist")
			return
	command = "tar -cpzf '{}' -C / '{}' ".format(compress_file, original_file[1:])
	# Execute command
	os.system(command)
	if (local_file_exist(compress_file)) and (int(get_file_size(compress_file)) > 0) :
		print ("--compressed"),
	else:
		print ("--original-file")
		os.system("cp {} {}".format(original_file, compress_file))
		return
	# Now we show the percentage of reduction
	reduction = get_files_size_diff(original_file, compress_file)
	print ("--reduction {}%".format(reduction))

	if settings['delete-after']:
		print ("--deleting-original")
		os.remove(original_file)

def verify_videos(settings, local_rel_path):
	local_rel_path_clean = local_rel_path.decode('utf-8').encode('utf-8')
	full_path = "{}{}".format(settings['local'], local_rel_path_clean)

	if is_video(local_rel_path):
		print ("Verifying video '{}' ".format(full_path)),
		# Create temporal file to keep the check result (we will remove it later)
		temp_file, temp_file_path = tempfile.mkstemp()
		command = "ffmpeg -v error -i '{}' -f null - 2>'{}'".format(full_path, temp_file_path)
		# Execute command
		result = os.system(command)
		# Check file size
		if (int(get_file_size(temp_file_path)) > 0):
			print ("--video-PROBLEM")
		else:
			print ("--video-OK")
		os.close(temp_file)





