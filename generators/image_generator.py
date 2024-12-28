import os
from io import BytesIO
from typing import Tuple
import time
import openai
import requests
from PIL import Image
from openai.error import RateLimitError

from data_models import StorySize


class ImageGenerator:
    @staticmethod
    def generate_image(prompt: str, story_size: StorySize, retries: int = 3, delay: int = 15) -> str:
        """
        Generate an image for the given prompt/sentence with retry logic to handle rate limits.

        Args:
            prompt: The text to generate an image for.
            story_size: Story size configuration.
            retries: Number of retry attempts in case of rate limit errors.
            delay: Delay (in seconds) between retry attempts.

        Returns:
            The URL for the generated image.

        Raises:
            Exception: If the image generation fails after all retries.
        """
        for attempt in range(retries):
            try:
                response = openai.Image.create(
                    prompt=prompt, 
                    n=1, 
                    size=story_size.image_part_size
                )
                url = response["data"][0]["url"]
                print(f"Generated image for prompt '{prompt}': {url}")
                return url
            except RateLimitError as e:
                print(f"Rate limit exceeded for prompt '{prompt}'. Retrying in {delay} seconds... ({attempt + 1}/{retries})")
                time.sleep(delay)

        # If all retries fail, raise an exception
        raise Exception(f"Failed to generate image for prompt '{prompt}' after {retries} attempts.")

    @staticmethod
    def download_image(
        workdir: str, url: str, image_number: str
    ) -> Tuple[Image.Image, str]:
        """Download the image from the given url

        Args:
            workdir: The workdir where to download the image
            url: The url of the image to download
            image_number: The number of the image in the story sequence

        Returns: A pair of Image object and image file path
        """
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        filepath = os.path.join(workdir, f"image_{image_number}.png")
        img.save(filepath)
        return img, filepath
