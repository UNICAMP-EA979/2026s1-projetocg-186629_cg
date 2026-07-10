import glob
import os


def clear_workdir(name: str, dir: str = "", image_only: bool = False):

    basename = os.path.join(dir, name)

    paths = []
    paths += glob.glob(basename+"*.png")

    if not image_only:
        paths += glob.glob(basename+"*.mp4")

    for path in paths:
        os.remove(path)
