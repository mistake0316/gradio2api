from setuptools import setup, find_packages

setup(
  name="gradio2api",
  version="0.0.2",
  description="Transfer gradio application to fastapi.",
  url="https://github.com/mistake0316/gradio2api",
  author="湯沂達(Tang Yi Dar)",
  author_email="changethewhat@gmail.com",
  license="MIT",
  packages=find_packages(),
  install_requires=[
    "fastapi[standard]",
    "gradio_client",
    "gradio",
  ],
  classifiers=[
    "License :: OSI Approved :: MIT License",
  ],
  python_requires=">=3.9"
)