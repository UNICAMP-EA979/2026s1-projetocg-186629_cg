import glob
import os

import cv2 as cv


def image_to_video(basename: str,
                   dir: str = "",
                   fps: float = 2.0):
    paths = glob.glob(os.path.join(dir, f"{basename}*.png"))
    paths = sorted(paths)

    img = cv.imread(paths[0])
    if img is None:
        raise RuntimeError(f"Invalid basename {basename}")

    height = img.shape[0]
    width = img.shape[1]

    fourcc = cv.VideoWriter_fourcc(*'mp4v')  # type: ignore
    writer = cv.VideoWriter(os.path.join(
        dir, f"{basename}.mp4"), fourcc, fps, (width, height))

    for path in paths:
        frame = cv.imread(path)
        if frame is None:
            raise RuntimeError(f"Invalid image {path}")

        writer.write(frame)

    writer.release()
