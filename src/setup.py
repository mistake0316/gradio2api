from setuptools import setup, find_packages

setup(
  name="gradio_client_fastapi",
  version="0.0.1",
  description="Transfer gradio application to fastapi applicaiton.",
  url="https://github.com/mistake0316/gradio_client_fastapi",
  author="Tang Yi Dar",
  author_email="changethewhat@gmail.com",
  license="MIT",
  packages=find_packages(),
  install_requires=[
    "fastapi",
    "gradio_client",
    "gradio",
  ],
  classifiers=[
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Operating System :: OS Independent",
  ],
  python_requires=">=3.9"
)