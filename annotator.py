from gradio_client import Client
from typing import List, Dict, Any, Union, Literal

from gr_types import LOWER_PARAMETER_TYPES, LOWER_RETURN_TYPES

def gr_parameter_to_pydantic_model(L:list[dict]):
  
  __model_annotations = {}

  for parameter_dict in L:
    __D = parameter_dict

    _label=__D.get("label")
    _parameter_name=__D.get("parameter_name")
    _parameter_has_default=__D.get("parameter_has_default")
    _parameter_default=__D.get("parameter_default")
    _type=__D.get("type")
    _python_type=__D.get("python_type")
    _example_input=__D.get("example_input")
    _component :str = __D.get("component")
    
    component_type = LOWER_PARAMETER_TYPES[_component.lower()]
    

c = Client("https://73b62eaef47a0596bf.gradio.live/")
