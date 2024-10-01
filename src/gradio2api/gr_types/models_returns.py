import numpy as np
from pydantic import BaseModel, ConfigDict
from typing import List
from typing_extensions import Literal, Any, Optional, NotRequired
from datetime import datetime
import PIL
import PIL.Image
from pathlib import Path
# ------
from gradio.data_classes import FileData
from gradio.components.plot import (
  AltairPlotData as value_AltairPlotData,
  PlotData as G_PlotData
)
from gradio.components.paramviewer import Parameter
from gradio.components.label import LabelData

from gradio.components.highlighted_text import HighlightedToken

# ------
FILE = str
# ------
# class _Chatbot(BaseModel):
#   message: Optional[str]
#   chat_history: Optional[tuple[str]]

class _Dataframe(BaseModel):
  headers: list[str]
  data: list[list[Any]]| list[tuple[Any, ...]]
  metadata: Optional[dict[str, Optional[list[Any]]]] = None

class AltairPlotData(BaseModel):
  value: value_AltairPlotData
  model_config = ConfigDict(extra="allow")

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

class _Video(BaseModel):
  video: FILE
  subtitles: FILE | None = None
# ------
from gradio.data_classes import GradioRootModel
def get_root_type_of_T(T:GradioRootModel):
  return T.model_fields["root"].annotation

# ------
AnnotatedImage = tuple[str, list[tuple[str, str]]] | None
Audio = FILE
Barplot = AltairPlotData
Button = str | None
Chatbot = (
  list[list[str | tuple[str] | tuple[str, str] | None]]
| Any # | list[Message] # TODO: need to coding
| None
)
Checkbox = bool | None
CheckboxGroup = list[str | int | float] | str | int | float | None
ClearButton = str | None
Code = str | None
Colorpicker = str | None
Dataframe = _Dataframe
Dataset = int | None
Datetime = float | datetime | str | None
Downloadbutton = FILE | None
Dropdown = str | int | float | list[str | int | float] | None
DuplicateButton = str | None
File = FILE | list[FILE] | None
FileExplorer = str | list[str] | None
Gallery = list[_Gallery] | None
HighlightedText = list[HighlightedToken]
HTML = str | None
Image = FILE
ImageEditor = _ImageEditor | None
JSON = dict | list | str | None
Label = LabelData | dict | None
Lineplot = AltairPlotData
LoginButton = str | None
LogoutButton = str | None
Markdown = str | None
Model3D = FILE | None
MultimodalTextbox = _Multimodaltextbox | None
Number = float | int | None
ParamViewer = dict[str, Parameter]
Plot = G_PlotData
Radio = str | int | float | None
ScatterPlot = AltairPlotData
SimpleImage = FILE | None
Slider = float | None
State = Any
Textbox = str | None
Timer = float | None
UploadButton = str | list[str] | None
Video = _Video | None
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