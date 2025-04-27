"""
Image utilities for the presentation maker.
"""
import os
import re
import requests
import base64
import json
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse, quote_plus
import uuid

class ImageUtils:
    """
    Utilities for handling image search and processing.
    """

    @staticmethod
    def generate_image_search_query(slide_title: str, slide_content: str) -> str:
        """
        Generate a search query for finding relevant images based on slide content.

        Args:
            slide_title: The title of the slide
            slide_content: The content of the slide

        Returns:
            A search query for finding images
        """
        # Extract key concepts from the slide content
        # Remove markdown formatting
        clean_content = re.sub(r'[*_#>~`]', '', slide_content)

        # Extract key concepts
        concepts = ImageUtils.extract_key_concepts(slide_content, max_concepts=3)

        # Create a concise search query
        if concepts:
            query = f"{slide_title} {' '.join(concepts)} professional presentation image"
        else:
            # Fallback to using the title
            query = f"{slide_title} professional presentation image"

        return query

    @staticmethod
    def search_images_unsplash(query: str, per_page: int = 5) -> List[str]:
        """
        Search for images on Unsplash using their API.

        Args:
            query: Search query
            per_page: Number of results to return

        Returns:
            List of image URLs
        """
        # Use Unsplash Source API which doesn't require authentication
        # Format: https://source.unsplash.com/random?query
        image_urls = []

        # Encode the query for URL
        encoded_query = quote_plus(query)

        # Get multiple images by making multiple requests
        for _ in range(per_page):
            # Add a random parameter to avoid caching
            random_id = uuid.uuid4().hex[:8]
            url = f"https://source.unsplash.com/featured/?{encoded_query}&random={random_id}"

            try:
                # Make a request to get the redirected URL
                response = requests.get(url, allow_redirects=True, timeout=10)
                if response.status_code == 200:
                    # The final URL after redirection is the image URL
                    image_urls.append(response.url)
            except Exception as e:
                print(f"Error searching Unsplash: {e}")

        return image_urls

    @staticmethod
    def search_images_pexels(query: str, per_page: int = 5) -> List[str]:
        """
        Search for images on Pexels using their API.

        Args:
            query: Search query
            per_page: Number of results to return

        Returns:
            List of image URLs
        """
        # Use Pexels API
        api_key = os.environ.get("PEXELS_API_KEY")
        if not api_key:
            print("No Pexels API key found. Using alternative search method.")
            return []

        headers = {
            "Authorization": api_key
        }

        # Encode the query for URL
        encoded_query = quote_plus(query)
        url = f"https://api.pexels.com/v1/search?query={encoded_query}&per_page={per_page}"

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [photo["src"]["large"] for photo in data.get("photos", [])]
            else:
                print(f"Error searching Pexels: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error searching Pexels: {e}")
            return []

    @staticmethod
    def search_images_pixabay(query: str, per_page: int = 5) -> List[str]:
        """
        Search for images on Pixabay using their API.

        Args:
            query: Search query
            per_page: Number of results to return

        Returns:
            List of image URLs
        """
        # Use Pixabay API
        api_key = os.environ.get("PIXABAY_API_KEY")
        if not api_key:
            print("No Pixabay API key found. Using alternative search method.")
            return []

        # Encode the query for URL
        encoded_query = quote_plus(query)
        url = f"https://pixabay.com/api/?key={api_key}&q={encoded_query}&image_type=photo&per_page={per_page}"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [hit["largeImageURL"] for hit in data.get("hits", [])]
            else:
                print(f"Error searching Pixabay: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error searching Pixabay: {e}")
            return []

    @staticmethod
    def search_images(query: str, per_page: int = 5) -> List[str]:
        """
        Search for images using multiple sources.

        Args:
            query: Search query
            per_page: Number of results to return from each source

        Returns:
            List of image URLs
        """
        # Try multiple sources and combine results
        image_urls = []

        # Try Unsplash (no API key required)
        unsplash_urls = ImageUtils.search_images_unsplash(query, per_page)
        image_urls.extend(unsplash_urls)

        # If we don't have enough images, try Pexels
        if len(image_urls) < per_page:
            pexels_urls = ImageUtils.search_images_pexels(query, per_page - len(image_urls))
            image_urls.extend(pexels_urls)

        # If we still don't have enough images, try Pixabay
        if len(image_urls) < per_page:
            pixabay_urls = ImageUtils.search_images_pixabay(query, per_page - len(image_urls))
            image_urls.extend(pixabay_urls)

        # Return unique URLs
        return list(set(image_urls))

    @staticmethod
    def download_image(image_url: str, save_dir: str = "images") -> Optional[str]:
        """
        Download an image from a URL and save it locally.

        Args:
            image_url: URL of the image to download
            save_dir: Directory to save the image in

        Returns:
            Path to the saved image or None if download failed
        """
        # Create the directory if it doesn't exist
        os.makedirs(save_dir, exist_ok=True)

        try:
            # For base64 encoded images
            if image_url.startswith('data:image'):
                # Extract the base64 data
                image_data = image_url.split(',')[1]
                image_binary = base64.b64decode(image_data)

                # Generate a filename
                filename = f"{uuid.uuid4()}.png"
                filepath = os.path.join(save_dir, filename)

                # Save the image
                with open(filepath, 'wb') as f:
                    f.write(image_binary)

                return filepath

            # For URL images
            else:
                response = requests.get(image_url, stream=True, timeout=10)
                response.raise_for_status()

                # Get filename from URL or generate one
                parsed_url = urlparse(image_url)
                filename = os.path.basename(parsed_url.path)
                if not filename or '.' not in filename:
                    filename = f"{uuid.uuid4()}.jpg"

                filepath = os.path.join(save_dir, filename)

                # Save the image
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                return filepath

        except Exception as e:
            print(f"Error downloading image: {e}")
            return None

    @staticmethod
    def add_image_to_slide_markdown(slide_content: str, image_path: str, alt_text: str = "Slide illustration") -> str:
        """
        Add an image to a slide in markdown format.

        Args:
            slide_content: The original slide content
            image_path: Path to the image
            alt_text: Alternative text for the image

        Returns:
            Updated slide content with the image
        """
        # Create the markdown image tag
        image_markdown = f"\n\n![{alt_text}]({image_path})\n\n"

        # Add the image at the beginning of the slide content
        return image_markdown + slide_content

    @staticmethod
    def extract_key_concepts(slide_content: str, max_concepts: int = 5) -> List[str]:
        """
        Extract key concepts from slide content.

        Args:
            slide_content: The slide content
            max_concepts: Maximum number of concepts to extract

        Returns:
            List of key concepts
        """
        # Remove markdown formatting
        clean_content = re.sub(r'[*_#>~`]', '', slide_content)

        # Extract bullet points
        bullet_points = re.findall(r'^\s*(?:\*|\+|-)\s+(.*?)$', clean_content, re.MULTILINE)

        # If we have bullet points, use them as concepts
        if bullet_points:
            # Take the first few bullet points
            concepts = bullet_points[:max_concepts]
            # Clean up and return
            return [concept.strip() for concept in concepts if concept.strip()]

        # Otherwise, split by sentences and use those
        sentences = re.split(r'[.!?]\s+', clean_content)
        concepts = sentences[:max_concepts]

        return [concept.strip() for concept in concepts if concept.strip()]
