from find_more_like_algorithm.constants import CACHED_POSTER_IMAGES_LIMIT
from find_more_like_algorithm.utils import CACHED_POSTER_IMAGES_PATH


def _save_image(image_path, response_content):
    with image_path.open("wb") as image_file:
        image_file.write(response_content)


def _get_cached_image_path(imdb_id):
    image_path = CACHED_POSTER_IMAGES_PATH.joinpath(f"{imdb_id}.png")
    return image_path


def delete_oldest_cached_image_if_cached_poster_images_limit_reached():
    cached_images_paths = list(CACHED_POSTER_IMAGES_PATH.glob("*.png"))
    if len(cached_images_paths) > CACHED_POSTER_IMAGES_LIMIT:
        sorted_cached_images_paths = sorted(cached_images_paths, key=get_path_modification_time)
        oldest_oldest_cached_image_path = sorted_cached_images_paths[0]
        oldest_oldest_cached_image_path.unlink()


def get_path_modification_time(path):
    return path.stat().st_mtime
