"""
Setup script for Arvos Python SDK
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="arvos-sdk",
    version="1.0.0",
    author="Jaskirat Singh",
    author_email="jaskirat1616@gmail.com",
    description="Python SDK for receiving sensor data from Arvos iPhone app",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jaskirat1616/arvos-sdk",
    packages=find_packages(where="python"),
    package_dir={"": "python"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "websockets>=11.0",
        "qrcode[pil]>=7.4",
        "numpy>=1.20.0",
    ],
    extras_require={
        "visualization": ["matplotlib>=3.5.0"],
        "image": ["Pillow>=9.0.0", "opencv-python>=4.5.0"],
        "ros2": ["rclpy", "cv_bridge"],
        "dev": ["pytest>=7.0.0", "black>=22.0.0", "flake8>=4.0.0"],
    },
)
