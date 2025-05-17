"""
Resource pack generation for the application.
"""

import json
import logging
import os
from typing import List, Optional

from ..utils.config import config
from ..utils.exceptions import ResourcePackError

logger = logging.getLogger(__name__)


def generate_resource_pack(json_files: List[str], page=None) -> bool:
    """
    Generate a resource pack with the given JSON files.
    
    Args:
        json_files: A list of JSON file paths to include in the resource pack
        page: The UI page object (optional)
        
    Returns:
        True if the resource pack was generated successfully, False otherwise
        
    Raises:
        ResourcePackError: If the resource pack cannot be generated
    """
    try:
        # Check if pack format is set
        if config.pack_format is None:
            error_msg = "Pack format is not set. Please select a Minecraft version."
            logger.error(error_msg)
            return False
        
        # Create assets directory
        assets_dir = os.path.join(config.OUTPUT_DIR, "assets")
        os.makedirs(assets_dir, exist_ok=True)
        logger.info(f"Created/verified assets directory: {assets_dir}")
        
        # Get asset folder names
        asset_folders = [
            os.path.basename(os.path.dirname(os.path.dirname(json_file)))
            for json_file in json_files
        ]
        asset_folders_str = "、".join(asset_folders)
        
        # Create pack.mcmeta content
        pack_mcmeta_content = {
            "pack": {
                "pack_format": config.pack_format,
                "description": f"{asset_folders_str}を翻訳したリソースパックです。"
            }
        }
        
        # Write pack.mcmeta file
        pack_mcmeta_path = os.path.join(config.OUTPUT_DIR, "pack.mcmeta")
        with open(pack_mcmeta_path, "w", encoding="utf-8") as f:
            json.dump(pack_mcmeta_content, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Generated pack.mcmeta file: {pack_mcmeta_path}")
        return True
    
    except Exception as e:
        error_msg = f"Failed to generate resource pack: {str(e)}"
        logger.error(error_msg)
        raise ResourcePackError(error_msg) from e