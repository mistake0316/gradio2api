# from gr_types import LOWER_PARAMETER_TYPES, LOWER_RETURN_TYPES
from pydantic import BaseModel
from typing import Any, TypedDict
from typing_extensions import Optional

class PartParameter(TypedDict):
  label: str
  parameter_name: str
  parameter_has_default: bool
  parameter_default: str
  type: str
  python_type: str
  example_input: dict
  component: str

class PartReturn(TypedDict):
  label: str
  component: str

class Annotation(TypedDict):
  annotation: Any
  required: bool
  default: Optional[Any]

def make_annotator(J:PartParameter | PartReturn)->Annotation:
  return Annotation
