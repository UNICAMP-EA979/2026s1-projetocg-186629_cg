import os

last_i = -1


def get_filename_unique(filename: str, path: str = "", extension=".png") -> str:
    global last_i
    i = last_i+1
    new_path = os.path.join(path, filename+f"{i:03d}"+extension)
    while os.path.exists(new_path):
        i += 1
        new_path = os.path.join(path, filename+f"{i:03d}"+extension)

    last_i = i
    return new_path
