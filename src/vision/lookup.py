#!/usr/bin/python
# -*- coding: utf-8 -*-
import os.path
import glob
from configuration import configuration

root = "./"
def cache_path(name):
	return os.path.join(root, "cache", name) 

video_render_types = ["broadcast", "theora", "thumbs", "vc1"]
id_example_videos = [1302, 1303, 1343, 1344]


def _glob_path(media_root, video_id, render_type, video_filename_globs):
	for video_filename_glob in video_filename_globs:
		paths = [str(video_id), render_type, video_filename_glob]
		if "" in paths:
			paths.remove("")
		filename_glob = os.path.sep.join(paths)
		filename_glob = os.path.join(media_root, filename_glob)
		filename = glob.glob(filename_glob)
		if filename:
			break
	return filename

# TODO: Clean up this function. No, clean up the whole lookup-module
def get_library_filename_by_id(video_id, video_filename_globs=["*.avi", "*.mpg", "*.mov", "*.dv"]):
	# Then /media/video/1302/broadcast
	filename = _glob_path(configuration.media_root, video_id, configuration.render_type, video_filename_globs)
	if not filename:
		# Give up, but respond with a failure filename
		paths = [configuration.media_root, str(video_id), configuration.render_type, video_filename_globs]
		return os.path.sep.join(paths)	
	# Return first hit
	return filename[0]

# TODO: rename to locate_media_by_id? 
def build_path(video_id, video_filename_globs=["*.avi", "*.mpg", "*.mov", "*.dv"]):
	# example path: "videos/1302/broadcast/"
	# First look at ./cache/video/1302/broadcast
	filename = _glob_path(configuration.video_cache_root, video_id, configuration.render_type, video_filename_globs)
	if not filename:
		# Then ./cache/video/1302/
		filename = _glob_path(configuration.video_cache_root, video_id, "", video_filename_globs)
	if not filename:
		# Then /media/video/1302/broadcast
		filename = _glob_path(configuration.media_root, video_id, configuration.render_type, video_filename_globs)
	if not filename:
		# Give up, but respond with a failure filename
		paths = [configuration.media_root, str(video_id), configuration.render_type, video_filename_globs]
                print paths
		return os.path.sep.join(paths)	
	# Return first hit
	return filename[0]
		
