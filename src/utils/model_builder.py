from pydantic import BaseModel, ConfigDict
from pydantic.main import create_model
from typing import Any, TypedDict, Callable
from typing_extensions import Optional, Any

from gr_types import LOWER_PARAMETER_TYPES, LOWER_RETURN_TYPES
from utils.names import AutoName

class IgnoreModel(BaseModel):
  model_config = ConfigDict(extra="ignore")

class PartParameter(IgnoreModel):
  label: str
  parameter_name: str
  parameter_has_default: bool
  parameter_default: Any
  component: str

class PartReturn(IgnoreModel):
  label: str
  component: str

class InnerAnnotation(BaseModel):
  annotation: Any
  required: bool
  default: Optional[Any] = None

def make_single_annotation(config:PartParameter | PartReturn)->tuple[str, InnerAnnotation]:
  D = config.model_dump()

  IS_INPUT = "parameter_name" in D
  NAME = D.get("parameter_name") if IS_INPUT else D.get("label")
  COMPONENT = D.get("component")

  LOWER_COMPONENT = COMPONENT.lower()
  LOWER_TYPE_REFERENCE = LOWER_PARAMETER_TYPES if IS_INPUT else LOWER_RETURN_TYPES

  __TYPE =LOWER_TYPE_REFERENCE.get(LOWER_COMPONENT)

  __A = dict()
  
  __A.update(dict(annotation=__TYPE))
  if IS_INPUT:
    REQUIRED = D.get("parameter_has_default")
    DEFAULT = D.get("parameter_default")
    __A.update(dict(required=REQUIRED))
    if REQUIRED:
      __A.update(dict(default=DEFAULT))
  else:
    REQUIRED = False
    __A.update(dict(required=REQUIRED))

  return NAME, InnerAnnotation(**__A)

def annotation_to_field(annotations:dict[str, InnerAnnotation]):
    fields = dict()
    for field_name, field_info in annotations.items():
        field_info_D = field_info.model_dump()
        annotation = field_info_D['annotation']
        default = ...
        if not field_info_D['required']:
            default = field_info_D['default']
        fields[field_name] = (annotation, default)
    return fields

def configs_list_to_model(
  configs=list[PartParameter] | list[PartReturn],
  model_name:Callable | str = AutoName().get_name,
)->BaseModel:
  model_name_callable = isinstance(model_name, Callable)
  if model_name_callable:
    model_name = model_name()
  
  total_annotation = dict()
  for config in configs:
    name, annotation = make_single_annotation(config)
    assert name not in total_annotation
    total_annotation[name] = annotation
  
  fields = annotation_to_field(total_annotation)

  return create_model(
    model_name,
    **fields
  )