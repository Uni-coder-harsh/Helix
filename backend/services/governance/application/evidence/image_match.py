def calculate_image_similarity(image_url1: str, image_url2: str) -> float:
    """Mock perceptual similarity comparison of image paths/contents."""
    if not image_url1 or not image_url2:
        return 0.0
    if image_url1 == image_url2:
        return 1.0
    # Match basename
    if image_url1.split("/")[-1] == image_url2.split("/")[-1]:
        return 0.95
    return 0.5
