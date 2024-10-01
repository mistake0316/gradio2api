import numpy as np
from pydantic import BaseModel
from typing_extensions import Literal, Any, Optional
from datetime import datetime
import PIL.Image
# ------
from gradio.components.image_editor import EditorValue
from gradio.components.multimodal_textbox import MultimodalValue
from gradio.components.paramviewer import Parameter
# ------
class FILE(BaseModel):
  path:str
  def to_handle_file(self):
    from gradio_client import handle_file
    return handle_file(self.path)
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

class _ImageEditor(BaseModel):
  background: FILE
  layers: list[FILE]
  composite: FILE | None
  id: str | None

class _Multimodaltextbox(BaseModel):
  text: str
  files: list[FILE]

class _Video(BaseModel):
  video:FILE
# ------
AnnotatedImage = tuple[str, list[tuple[str, str]]] | None
Audio = FILE
Barplot = _AltairPlotData
Button = str | None
Chatbot = _Chatbot
Checkbox = bool | None
CheckboxGroup = list[str | int | float] | list[int | None]
ClearButton = str | None
Code = str | None
Colorpicker = str | None
Dataframe = _Dataframe
Dataset = int | list | None
Datetime = float | datetime | str | None
Downloadbutton = str | None
Dropdown = str | int | float | list[str | int | float] | list[int | None] | None
DuplicateButton = str | None
File = bytes | str | list[bytes] | list[str] | None
FileExplorer = list[str] | str | None
Gallery = list[tuple[str, str]] | None
HighlightedText = list[tuple[str, str | float | None]] | None
HTML = str | None
Image = FILE
ImageEditor = _ImageEditor | None
JSON = dict | list | None
Label = dict[str, float] | str | int | float | None
Lineplot = _AltairPlotData
LoginButton = str | None
LogoutButton = str | None
Markdown = str | None
Model3D = str | None
MultimodalTextbox = _Multimodaltextbox
Number = float | int | None
ParamViewer = dict[str, Parameter]
Plot = _AltairPlotData
Radio = str | int | float | None
ScatterPlot = _AltairPlotData
SimpleImage = str | None
Slider = float
State = Any
Textbox = str | None
Timer = float | None
UploadButton = bytes | str | list[bytes] | list[str] | None
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