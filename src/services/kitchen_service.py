from pathlib import Path
import random
from typing import Tuple


async def get_people_on_kitchen() -> Tuple[int, Path]:
    temp_path = "src/files/kitchen_photo/kitchen_photo_temp.jpg"
    people_count = random.randint(0, 10)
    return (people_count, temp_path)
