import logging
from celery import shared_task
from PIL import Image, UnidentifiedImageError
from django.core.files.storage import default_storage

from .models import MediaAsset, ImageOptimizationProfile

logger = logging.getLogger(__name__)

@shared_task
def process_media_asset(asset_id):
    """
    Celery task to extract metadata and generate optimized versions for a MediaAsset.
    """
    try:
        asset = MediaAsset.objects.get(id=asset_id)
        logger.info(f"Processing media asset: {asset_id} ({asset.filename})")
    except MediaAsset.DoesNotExist:
        logger.error(f"MediaAsset with id {asset_id} not found.")
        return

    # --- Metadata Extraction ---
    try:
        if not asset.file:
            logger.warning(f"Asset {asset_id} has no file associated.")
            return

        # Get basic file info
        asset.size = asset.file.size
        # TODO: Get MIME type more reliably (e.g., using python-magic if installed)
        # For now, rely on Django's upload handling or filename extension
        # asset.mime_type = ...

        # Get image dimensions if it's an image
        if asset.file.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.avif')):
            try:
                asset.file.open('rb') # Ensure file is open
                with Image.open(asset.file) as img:
                    asset.width = img.width
                    asset.height = img.height
                    # asset.mime_type = Image.MIME.get(img.format) # Get MIME from Pillow
                asset.file.close() # Close file
            except UnidentifiedImageError:
                logger.warning(f"Could not identify image format for asset {asset_id}.")
            except Exception as e:
                logger.error(f"Error getting dimensions for asset {asset_id}: {e}")
                if asset.file.closed is False:
                    asset.file.close() # Ensure file is closed on error

        asset.save(update_fields=['size', 'width', 'height', 'mime_type'])
        logger.info(f"Metadata extracted for asset {asset_id}.")

    except Exception as e:
        logger.error(f"Error extracting metadata for asset {asset_id}: {e}")
        # Continue to optimization if possible? Or return?

    # --- Image Optimization ---
    if asset.is_image:
        logger.info(f"Starting image optimization for asset {asset_id}...")
        # TODO: Implement actual optimization logic
        # - Iterate through active ImageOptimizationProfile instances
        # - For each profile:
        #   - Open the original image with Pillow
        #   - Resize/crop/convert format/adjust quality based on profile settings
        #   - Construct new filename (e.g., <original_name>_<profile_name>.<format>)
        #   - Save the optimized version to storage (e.g., default_storage.save(...))
        #   - Get the URL of the saved optimized version
        #   - Update asset.optimized_versions JSON field with {profile.name: optimized_url}
        # Example placeholder:
        # asset.optimized_versions['thumbnail'] = asset.file_url # Replace with actual thumb URL
        # asset.save(update_fields=['optimized_versions'])
        logger.info(f"Placeholder: Image optimization complete for asset {asset_id}.")
    else:
        logger.info(f"Asset {asset_id} is not an image, skipping optimization.")