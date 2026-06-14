from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="ai-video-agent",
    version="0.1.0",
    author="Gilbert Ababono",
    description="AI Video Agent for uploading faceless videos to YouTube Shorts, TikTok, and Facebook Reels",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gilbertababono2-creator/ai-video-agent",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ai-video-agent=agent.cli:main",
        ],
    },
)
