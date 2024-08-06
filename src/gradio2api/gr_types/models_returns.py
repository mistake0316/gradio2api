import numpy as np
from pydantic import BaseModel
from typing import List
from typing_extensions import Literal, Any, Optional
from datetime import datetime
import PIL
import PIL.Image
from pathlib import Path
# ------
from gradio.components.gallery import GalleryImageType, CaptionedGalleryImageType
from gradio.components.image_editor import EditorValue, ImageType
from gradio.components.multimodal_textbox import MultimodalValue
from gradio.components.paramviewer import Parameter
# ------
FILE = str
# ------
class _Chatbot(BaseModel):
  message: Optional[str]
  chat_history: Optional[tuple[str]]

class _Dataframe(BaseModel):
  headers: Optional[list[str]]
  data: Optional[FILE]
  metadata: Optional[dict | None]

class _AltairPlotData(BaseModel):
  type: Literal["altair"]
  plot: str
  chart: str

class _Gallery(BaseModel):
  image:FILE
  caption:str | None

class _ImageEditor(BaseModel):
  background: FILE
  layers: list[FILE]
  composite: FILE | None
  id: str | None

class _Multimodaltextbox(BaseModel):
  text: str
  files: list[FILE]
# ------
AnnotatedImage = tuple[str, list[tuple[str, str]]] | None
Audio = FILE
Barplot = _AltairPlotData
Button = str | None
Chatbot = _Chatbot
Checkbox = bool | None
CheckboxGroup = list[str | int | float] | str | int | float | None
ClearButton = str | None
Code = tuple[str] | str | None
Colorpicker = str | None
Dataframe = _Dataframe
Dataset = list[list]
Datetime = float | datetime | str | None
Downloadbutton = str | Path | None
Dropdown = str | int | float | list[str | int | float] | None
DuplicateButton = str | None
File = str | list[str] | None
FileExplorer = str | list[str] | None
Gallery = list[_Gallery] | None
HighlightedText = list[tuple[str, str | float | None]] | dict | None
HTML = str | None
Image = FILE
ImageEditor = _ImageEditor | None
JSON = dict | list | str | None
Label = dict[str, float] | str | int | float | None
Lineplot = _AltairPlotData
LoginButton = str | None
LogoutButton = str | None
Markdown = str | None
Model3D = str | Path | None
MultimodalTextbox = _Multimodaltextbox
Number = float | int | None
ParamViewer = dict[str, Parameter]
Plot = _AltairPlotData
Radio = str | int | float | None
ScatterPlot = _AltairPlotData
SimpleImage = str | Path | None
Slider = float | None
State = Any
Textbox = str | None
Timer = float | None
UploadButton = str | list[str] | None
Video = str | Path | tuple[str | Path, str | Path | None] | None
# ------
TYPES = {
  "AnnotatedImage" : AnnotatedImage,
  "Audio" : Audio,
  "Barplot" : Barplot,
  "Button" : Button,
  "Chatbot" : Chatbot,
  "Checkbox" : Checkbox,
  "CheckboxGroup" : CheckboxGroup,
  "ClearButton" : ClearButton,
  "Code" : Code,
  "Colorpicker" : Colorpicker,
  "Dataframe" : Dataframe,
  "Dataset" : Dataset,
  "Datetime" : Datetime,
  "Downloadbutton" : Downloadbutton,
  "Dropdown" : Dropdown,
  "DuplicateButton" : DuplicateButton,
  "File" : File,
  "FileExplorer" : FileExplorer,
  "Gallery" : Gallery,
  "HighlightedText" : HighlightedText,
  "HTML" : HTML,
  "Image" : Image,
  "ImageEditor" : ImageEditor,
  "JSON" : JSON,
  "Label" : Label,
  "Lineplot" : Lineplot,
  "LoginButton" : LoginButton,
  "LogoutButton" : LogoutButton,
  "Markdown" : Markdown,
  "Model3D" : Model3D,
  "MultimodalTextbox" : MultimodalTextbox,
  "Number" : Number,
  "ParamViewer" : ParamViewer,
  "Plot" : Plot,
  "Radio" : Radio,
  "ScatterPlot" : ScatterPlot,
  "SimpleImage" : SimpleImage,
  "Slider" : Slider,
  "State" : State,
  "Textbox" : Textbox,
  "Timer" : Timer,
  "UploadButton" : UploadButton,
  "Video" : Video,
}