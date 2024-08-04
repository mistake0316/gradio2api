from pydantic import BaseModel, ConfigDict
from pydantic.main import create_model
from typing import Any, TypedDict, Callable, Literal
from types import EllipsisType
from typing_extensions import Optional, Any

from gradio_client import Client
from gradio_client.client import DEFAULT_TEMP_DIR as GR_DEFAULT_TEMP_DIR
from gradio_client.utils import (
  sanitize_parameter_names,
  sanitize_parameter_names as sanitize_return_names,
)

from ..gr_types import LOWER_PARAMETER_TYPES, LOWER_RETURN_TYPES
from ..gr_types.models_parameters import FILE as FILE_INPUT
from copy import deepcopy

import functools

class IgnoreModel(BaseModel):
  model_config = ConfigDict(extra="ignore")

class PartGradioField(IgnoreModel):
  label: str
  component: str

class PartReturn(PartGradioField):
  ...

class PartParameter(PartGradioField):
  parameter_name: str
  parameter_has_default: bool
  parameter_default: Any

class InnerAnnotation(BaseModel):
  annotation: Any
  required: bool
  default: Optional[Any] = None

class BaseField:
  name:str
  annotation:Any
  required:bool
  default:bool | EllipsisType

  def __init__(
      self,
      config:PartReturn | PartParameter,
      allow_not_in_reference=True,
    ):
    self.config = deepcopy(config)
    self.allow_not_in_reference = allow_not_in_reference
    self.preprocess()
    self.validate()

  @property
  def _config_dict(self):
    return self.config.model_dump()

  @property
  def _gr_component(self):
    return self.config.component
  
  def get_gr_type(self, reference:dict = None, preprocesser: Callable | None =None):
    if reference is None:
      raise ValueError(f"reference should have value")
    
    assert (preprocesser is None) or isinstance(preprocesser, Callable)
    key = self._gr_component
    if preprocesser:
      key = preprocesser(key)
    
    assert (self.allow_not_in_reference) or (key in reference)
    return reference.get(key, Any)

  def preprocess(self):
    raise NotImplementedError("should be defined")

  def validate(self):
    for attribute_name in ["name", "annotation", "required", "default"]:
      assert hasattr(self, attribute_name)

  @property
  def _single_annotation(self)->dict[str, InnerAnnotation]:
    return {
      self.name: InnerAnnotation(
        annotation=self.annotation,
        required=self.required,
        default=self.default,
      )
    }

  def to_field_dict(self)->dict:
    single_field_dict = dict()
    for field_name, field_info in self._single_annotation.items():
        field_info_D = field_info.model_dump()
        annotation = field_info_D['annotation']
        default = ...
        if not field_info_D['required']:
            default = field_info_D['default']
        single_field_dict[field_name] = (annotation, default)
    return single_field_dict

class ParameterField(BaseField):
  def __init__(self, config:PartParameter):
    super().__init__(config) 

  def preprocess(self):
    self.name=sanitize_parameter_names(self.config.parameter_name)
    self.annotation = self.get_gr_type(
      reference=LOWER_PARAMETER_TYPES,
      preprocesser=str.lower
    )
    self.required = not self._config_dict.get("parameter_has_default")
    self.default = self._config_dict.get("parameter_default", ...)

class ReturnField(BaseField):
  def __init__(self, config:PartReturn):
    super().__init__(config)

  def preprocess(self):
    self.name=sanitize_return_names(self.config.label)
    self.annotation = self.get_gr_type(
      reference=LOWER_RETURN_TYPES,
      preprocesser=str.lower
    )
    self.required = True
    self.default = ...

ACCEPT_FIELD_TYPE = ReturnField | ParameterField | PartReturn | PartParameter | dict
class MultipleFields:
  def __init__(
      self,
      list_fields: list[ACCEPT_FIELD_TYPE]
    ):
    self.list_fields = self.normalize_list_fields(list_fields)
  
  @classmethod
  def normalize_list_fields(cls, list_fields:list[ACCEPT_FIELD_TYPE]):
    fields = [
      cls.normalize_field(field)
      for field in list_fields
    ]
    return fields
  
  @classmethod
  def normalize_field(cls, field:ACCEPT_FIELD_TYPE):
    do_nothing = lambda elem: elem
    def dict_to_field(D):
      IS_PARAMETER = D.get("parameter_name", False)
      IS_RETURN = IS_PARAMETER == False
      if IS_PARAMETER:
        P = PartParameter(**D)
        F = ParameterField(P)
      elif IS_RETURN:
        R = PartReturn(**D)
        F = ReturnField(R)
      else:
        raise RuntimeError()
      return F
    
    return_field = {
      ReturnField: do_nothing,
      ParameterField: do_nothing,
      PartReturn: ReturnField,
      PartParameter: ParameterField,
      dict: dict_to_field
    }[type(field)](field)

    return return_field
  
  def to_pydantic_model(self, model_name:str)->type[BaseModel]:
    fields_dict = {}
    for F in self.list_fields:
      _single_field_dict = F.to_field_dict()
      assert len(_single_field_dict) == 1 and list(_single_field_dict.keys())[0] not in fields_dict
      for key, val in _single_field_dict.items():
        fields_dict[key] = val
    
    return create_model(
      model_name,
      **fields_dict,
    )


class GradioAPI:
  def __init__(
    self,
    api_name:str,
    config_dict:dict,
    prefix:str,
    *,
    client:Client | None = None
  ):
    self.api_name = api_name
    self.__config_dict = deepcopy(config_dict)
    self.parameters = deepcopy(config_dict["parameters"])
    self.returns = deepcopy(config_dict["returns"])
    self.prefix = prefix

    self.__client = client
  

  def __verify_in_gr_client(self):
    assert self.client is not None
    assert self.api_name in self.view_api(
      return_format="dict"
    )["named_endpoints"]

  def __verify_same_config(self):
    raise NotImplementedError

  @functools.wraps(Client.view_api)
  def view_api(self, *args, **kwargs):
    assert self.client is not None
    return self.client.view_api(*args, **kwargs)

  @property
  def client(self)->Client:
    return self.__client

  @property
  def config_dict(self):
    return deepcopy(self.__config_dict)

  @property
  def parameter_model(self)->type[BaseModel]:
    return (
      MultipleFields(self.parameters)
      .to_pydantic_model(f"{self.prefix}{self.normalized_api_name}_parameter")
    )

  @property
  def return_model(self)->type[BaseModel]:
    return (
      MultipleFields(self.returns)
      .to_pydantic_model(f"{self.prefix}{self.normalized_api_name}_return")
    )

  @property
  def normalized_api_name(self):
    return self.api_name.replace("/","_")

  def normalize_input(self, item): # will return dict
    if type(item) is dict:
      item = self.parameter_model(**item)
    
    # TODO: handling file trasfer between gradio and fastapi
    def dfs_helper(item):
      if not isinstance(item, BaseModel):
        return item
      if item.__class__ is FILE_INPUT:
        return FILE_INPUT.to_handle_file(item)
      ret = dict()
      for key in item.model_fields.keys():
        ret[key] = dfs_helper(getattr(item, key))
      return ret
    
    return dfs_helper(item)
  
  def normalize_output(self, gr_result): # will return self.retun_model type
    ONLY_1_OUTPUT = len(self.returns) == 1
    if ONLY_1_OUTPUT:
      gr_result = [gr_result]
    
    D = {
      sanitize_return_names(R["label"]): field_result
      for R, field_result in zip(self.returns, gr_result)
    }
    return self.return_model(**D)

  def predict(self, item, return_fomat:Literal["list", "dict"]="dict"):
    assert self.client is not None
    item = self.normalize_input(item)
    
    gr_client : Client = self.client

    gr_result = gr_client.predict(
      **item,
      api_name=self.api_name,
    )
    if return_fomat == "list":
      return gr_result
    elif return_fomat == "dict":
      return self.normalize_output(gr_result)
    else:
      raise ValueError


  def __repr__(self) -> str:
    return "\n\n".join([
      Client._render_endpoints_info(
        None,
        self.api_name,
        self.config_dict,
      )
    ])

  def __call__(self, item):
    return self.predict(item)

class RemoteGradioApplication:
  src:str
  client_docuemnt:str
  client_info_dict:dict
  apis:dict[str, GradioAPI]
  prefix:str

  def __init__(
    self,
    src:str,
    prefix:str="",
    **gr_client_kwargs,
  ):
    client_kwargs = {
      "src":src,
      **gr_client_kwargs,
    }
    self.prefix = prefix

    self.__client = Client(
      **client_kwargs
    )

    self._preapre_apis()

  @property
  def client(self):
    return self.__client

  def _preapre_apis(self):
    self.client.view_api() # print information 
    self.client_docuemnt = self.client.view_api(
      print_info=False,
      return_format="str",
    )

    self.client_info_dict = self.client.view_api(
      print_info=False,
      return_format="dict",
    )

    self.__apis = {
      api_name:GradioAPI(
        api_name=api_name,
        config_dict=config_dict,
        prefix=f"{self.prefix}_",
        client=self.client,
      )
      for api_name, config_dict in self.client_info_dict["named_endpoints"].items()
    }
  
  @property
  def apis(self)->dict[str,GradioAPI]:
    return self.__apis

