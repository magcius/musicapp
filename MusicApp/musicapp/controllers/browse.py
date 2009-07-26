import logging

import os
import mutagen

from pylons import cache, config, request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from musicapp.lib.base import BaseController, render

log = logging.getLogger(__name__)

def validate_path(path):
    if path.startswith('..'):
        return False
    if path.startswith('%2e'):
        return False
    return True

def recur_dir_items(D):
    L = []
    for key, value in sorted(D.items()):
        L.append((key.decode('utf8'), value[0].decode('utf8'), recur_dir_items(value[1])))
    return L

media_path = os.path.abspath(config["media.path"])

def create_dir_items():
    print "YES!"
    dirs = {media_path: ("", {})}
    for root, a, b in os.walk(media_path):
        if root == media_path:
            continue
        parent, dirname = os.path.split(root)
        dirs[root] = dirs[parent][1][dirname] = (root[len(media_path)+1:], {})
        
    dir_items = recur_dir_items(dirs[media_path][1])

media_cache = cache.get_cache('media', type='file')
dir_items = media_cache.get_value('dir_items', createfunc=create_dir_items, expiretime=3600)

class BrowseController(BaseController):

    def directory(self, path=""):
        if not validate_path(path):
            abort(500, "Nice try...")
            
        c.dir_items = dir_items
        fullpath = os.path.abspath(os.path.join(media_path, path))
        
        if os.path.isdir(fullpath):
            
            c.path = path.strip("/")
            c.dirname = path.split("/")[-1]
            parent = unicode("/".join(path.split("/")[:-1]))
            c.files = [(u"../", parent, u"up", os.stat(os.path.split(fullpath)[0]))]
            
            for filename in sorted(os.listdir(fullpath)):
                serverpath = '%s/%s' % (c.path, filename)
                fullfile = os.path.join(fullpath, filename)
                filename = unicode(filename)
                if os.path.isdir(fullfile):
                    icon = "folder"
                elif filename.endswith((".jpg", ".gif", ".jpeg", ".png")):
                    icon = "image"
                elif filename.endswith((".mp3", ".aac", ".mp4", ".m4a", ".ogg", ".flac", ".wav")):
                    icon = "music"
                else:
                    icon = "file"
                c.files.append((filename, serverpath, icon, os.stat(fullfile)))
            return render('/browse_folder.jinja')
        elif os.path.isfile(fullpath):
            metadata = mutagen.File(fullpath, easy=True)
            if metadata is not None:
                c.artist = metadata['artist'][0]
                c.album  = metadata['album'][0]
                c.title  = metadata['title'][0]
                return render('/browse_file_music.jinja')
