#coding:utf-8


from django.conf import settings
import os


def clean_headfile_cache(verbose=False):
    """ delete all cache files in cache directory """
    def delete_tree(path):
        if not os.path.isdir(path):
            return

        for dir_item in os.listdir(path):
            fullpath = os.path.join(path, dir_item)
            if os.path.isfile(fullpath):
                os.remove(fullpath)
            elif os.path.isdir(fullpath):
                delete_tree(fullpath)
                os.rmdir(fullpath)

    pylucid_cache_path = os.path.join(
        settings.MEDIA_ROOT,
        settings.PYLUCID.PYLUCID_MEDIA_DIR,
        settings.PYLUCID.CACHE_DIR
    )
    if verbose:
        print "delete tree: %s " % pylucid_cache_path,
    delete_tree(pylucid_cache_path)
    if verbose:
        print "OK"
