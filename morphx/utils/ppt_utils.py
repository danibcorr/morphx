# Standard libraries
import logging
import re


def validate_slide_content(content: str, logger: logging.Logger | None) -> None:
    """
    Validates the structure of slide content based on the expected pattern.

    Args:
        content (str): The multi-slide content to validate.
        logger: A logger object to record validation messages.

    Returns:
        bool: True if all slides match the expected pattern, False otherwise.
    """

    try:
        # Pattern to split slides
        slides = re.split(r'###\s*\*?Slide\s+\d+\*?\s*\n', content)
        slides = [s.strip() for s in slides if s.strip()]
        
        if not slides:
            logger.error("No slides found in the content.")
            return False

        valid = True
        slide_number = 1

        for slide in slides:
            logger.info(f"Validating Slide {slide_number}...")

            # Check Identifier
            if not re.search(r"Identifier:\s*`[^`]+`", slide):
                logger.error(f"Slide {slide_number}: Missing or malformed Identifier.")
                valid = False

            # Check Main Title
            if not re.search(r"Main Title:\s*.+", slide):
                logger.error(f"Slide {slide_number}: Missing Main Title.")
                valid = False

            # Check Subtitle
            if not re.search(r"Subtitle:\s*.+", slide):
                logger.error(f"Slide {slide_number}: Missing Subtitle.")
                valid = False

            # Check Key Points header
            if not re.search(r"Key Points and Description:", slide):
                logger.error(f"Slide {slide_number}: Missing 'Key Points and Description' section.")
                valid = False
            else:
                # Check numbered points and bullets
                points = re.findall(r"\n\d+\.\s+.+", slide)
                if not points:
                    logger.error(f"Slide {slide_number}: No numbered key points found.")
                    valid = False
                else:
                    # Inside the loop over points
                    for i, point in enumerate(points, 1):
                        # Match bullet points possibly separated by blank lines or spaces
                        bullet_block = re.search(
                            rf"{re.escape(point)}(\n\s*\* .+)+",  # Allow blank lines and spaces before bullets
                            slide,
                            re.MULTILINE
                        )
                        if not bullet_block:
                            logger.warning(f"Slide {slide_number}, Point {i}: No bullet points found.")

            slide_number += 1

        logger.info("All slides match the expected pattern.")
    
    except ValueError:
        logger.warning("Some slides did not match the expected pattern.")
