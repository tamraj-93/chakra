#!/usr/bin/env python3
"""
Dependency resolver for Python packages with compatibility issues.

This script checks for incompatibilities and installs required versions.
This script resolves compatibility issues between Python dependencies
in the Chakra backend, particularly handling conflicts between
huggingface_hub and sentence_transformers packages.

Usage:
    python resolve_dependencies.py
"""

import os
import sys
import logging
import subprocess
import pkg_resources
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Define compatible package versions
COMPATIBLE_VERSIONS = {
    "sentence-transformers": "2.2.2",
    "huggingface_hub": "0.21.4",  # This version works with sentence-transformers 2.2.2
    "transformers": "4.31.0",     # Compatible with both packages above
    "langchain": "0.0.267",
    "langchain_text_splitters": "0.0.1"
}

# Environment variables
DEMO_MODE = os.environ.get("DEMO_MODE", "false").lower() == "true"
LIGHTWEIGHT_MODE = os.environ.get("CHAKRA_LIGHTWEIGHT_MODE", "false").lower() == "true"

def get_installed_versions() -> Dict[str, str]:
    """Get currently installed versions of packages"""
    installed = {}
    for package in COMPATIBLE_VERSIONS:
        try:
            installed[package] = pkg_resources.get_distribution(package).version
        except pkg_resources.DistributionNotFound:
            installed[package] = None
    return installed

def check_compatibility(installed: Dict[str, str]) -> List[Tuple[str, str]]:
    """Check if installed packages are compatible"""
    to_install = []
    
    for package, required_version in COMPATIBLE_VERSIONS.items():
        if installed.get(package) != required_version:
            to_install.append((package, required_version))
    
    return to_install

def install_packages(packages: List[Tuple[str, str]]) -> bool:
    """Install packages with specific versions"""
    if not packages:
        logger.info("All required packages are already installed with compatible versions")
        return True
    
    success = True
    for package, version in packages:
        package_spec = f"{package}=={version}"
        logger.info(f"Installing {package_spec}")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                package_spec, "--no-cache-dir"
            ])
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install {package_spec}: {e}")
            success = False
            # Only exit on failure if not in demo mode
            if not DEMO_MODE:
                return False
    
    return success

def install_pytorch():
    """Install PyTorch with CPU support"""
    if LIGHTWEIGHT_MODE:
        logger.info("Skipping PyTorch installation in lightweight mode")
        return True
    
    logger.info("Installing PyTorch (CPU version)")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "--no-cache-dir",
            "torch==2.0.1+cpu", 
            "torchvision==0.15.2+cpu",
            "--index-url", "https://download.pytorch.org/whl/cpu"
        ])
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install PyTorch: {e}")
        # Only exit on failure if not in demo mode
        if not DEMO_MODE:
            return False
        return True

def main():
    """Main function"""
    logger.info("Starting dependency resolution")
    
    # In demo or lightweight mode, we skip installing ML packages
    if DEMO_MODE or LIGHTWEIGHT_MODE:
        logger.info("Running in demo/lightweight mode, skipping ML package installation")
        return
    
    # Install PyTorch
    if not install_pytorch():
        logger.error("Failed to install PyTorch")
        sys.exit(1)
    
    # Check and install other dependencies
    installed = get_installed_versions()
    to_install = check_compatibility(installed)
    
    if install_packages(to_install):
        logger.info("Successfully resolved all dependencies")
    else:
        logger.error("Failed to install some dependencies")
        sys.exit(1)

if __name__ == "__main__":
    main()