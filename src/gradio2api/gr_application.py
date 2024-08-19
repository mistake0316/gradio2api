from pydantic import BaseModel, ConfigDict, Field
from pydantic.main import create_model
from typing import Any, TypedDict, Callable, Literal, _LiteralGenericAlias
from types import EllipsisType

from typing_extensions import Optional, Any

from gradio_client import Client
from gradio_client.client import DEFAULT_TEMP_DIR as GR_DEFAULT_TEMP_DIR
from gradio_client import utils as gr_client_utils
from gradio_client.utils import (
  sanitize_parameter_names,
  sanitize_parameter_names as sanitize_return_names,
)
import gradio as gr
from gradio import utils as gr_utils
from gradio.data_classes import JsonData

from .gr_types import LOWER_PARAMETER_TYPES, LOWER_RETURN_TYPES
from .gr_types.models_parameters import FILE as FILE_INPUT
from copy import deepcopy
from .utils.names import prefix_to_name
from gradio.exceptions import (
    GradioVersionIncompatibleError,
)
from packaging import version

import functools

class IgnoreModel(BaseModel):
  model_config = ConfigDict(extra="ignore")

class PythonType(BaseModel):
  type: str
  description: str

class PartGradioField(IgnoreModel):
  label: str
  component: str
  python_type: PythonType
  type: Any

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
  description: str = ""

class BaseField:
  name:str
  annotation:Any
  required:bool
  default:bool | EllipsisType
  description: str

  def __init__(
      self,
      config:PartReturn | PartParameter,
      allow_not_in_reference=True,
    ):
    self.config = deepcopy(config)
    self.allow_not_in_reference = allow_not_in_reference
    self.preprocess()
    self.__enumwise_annotation()
    self.validate()

  @property
  def _config_dict(self):
    return self.config.model_dump()

  @property
  def _gr_component(self):
    return self.config.component
  
  def get_gr_type(self, reference:dict = None, preprocesser: Callable | None = None):
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

  def __enumwise_annotation(self):
    my_type = self.config.type
    if enum := self.config.type.get("enum", None):
      self.annotation = _LiteralGenericAlias(Literal, tuple(enum))

    if self.config.type["type"] == "array":
      items = my_type.get("items", {})
      enum = items.get("enum", None)
      if enum:
        __L = _LiteralGenericAlias(Literal, tuple(enum))
        self.annotation = list[__L]

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
        description=self.description
      )
    }

  def to_field_dict(self)->dict:
    single_field_dict = dict()
    for field_name, field_info in self._single_annotation.items():
        field_info_D = field_info.model_dump()
        annotation = field_info_D['annotation']
        default = ...
        description = field_info_D['description']
        if not field_info_D['required']:
            default = field_info_D['default']
        single_field_dict[field_name] = (annotation, Field(default, description=description))
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
    self.description = self._config_dict.get("python_type", {}).get("description", "")

class ReturnField(BaseField):
  def __init__(self, config:PartReturn):
    super().__init__(config)

  def preprocess(self):
    self.name=sanitize_return_names(self.config.label)
    self.annotation = self.get_gr_type(
      reference=LOWER_RETURN_TYPES,
      preprocesser=str.lower,
    )
    self.required = True
    self.default = ...
    self.description = self._config_dict.get("python_type", {}).get("description", "")

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
  
  def to_pydantic_model(self, model_prefix:str)->type[BaseModel]:
    model_name = prefix_to_name(model_prefix)
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
    *,
    client:Client | None = None,
    app:gr.Blocks | None = None,
  ):
    self.api_name = api_name
    self.__config_dict = deepcopy(config_dict)
    self.parameters = deepcopy(config_dict["parameters"])
    self.returns = deepcopy(config_dict["returns"])

    assert not (
      (client != None)
      and
      (app != None)
    ), "only allow one of client or app"

    self.__client = client
    self.__app = app

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
  def app(self)->gr.Blocks:
    return self.__app

  @property
  def config_dict(self):
    return deepcopy(self.__config_dict)

  @property
  def parameter_model(self)->type[BaseModel]:
    return (
      MultipleFields(self.parameters)
      .to_pydantic_model(f"{self.normalized_api_name}_parameter")
    )

  @property
  def return_model(self)->type[BaseModel]:
    return (
      MultipleFields(self.returns)
      .to_pydantic_model(f"{self.normalized_api_name}_return")
    )

  @property
  def normalized_api_name(self):
    return self.api_name.replace("/","_")

  def normalize_input(self, item)->dict: # will return dict
    if type(item) is dict:
      item = self.parameter_model(**item)

    # TODO: handling file trasfer between gradio and fastapi
    def dfs_helper(item):
      if hasattr(item, "to_handle_file"):
        return item.to_handle_file()

      if not isinstance(item, BaseModel):
        return item

      ret = dict()
      for key in item.model_fields.keys():
        ret[key] = dfs_helper(getattr(item, key))
      return ret

    return dfs_helper(item)

  def normalize_output(self, gr_result:list): # will return self.retun_model type
    D = {
      sanitize_return_names(R["label"]): field_result
      for R, field_result in zip(self.returns, gr_result)
    }
    return self.return_model(**D)

  def predict_from_client(self, item, return_fomat:Literal["list", "dict"]="dict"):
    assert self.client is not None
    item = self.normalize_input(item)

    gr_client : Client = self.client

    gr_result = gr_client.predict(
      **item,
      api_name=self.api_name,
    )
    ONLY_1_OUTPUT = len(self.returns) == 1
    if ONLY_1_OUTPUT:
      gr_result = [gr_result]

    if return_fomat == "list":
      return gr_result
    elif return_fomat == "dict":
      return self.normalize_output(gr_result)
    else:
      raise ValueError

  def predict_from_app(self, item, return_fomat:Literal["list", "dict"]="dict"):
    assert self.app is not None
    item = self.normalize_input(item)
    item = self.parameter_model(**item)
    def dfs_unwrapper(item):
      if item.__class__ == FILE_INPUT:
        return item.path
      elif isinstance(item, BaseModel):
        return {
          key:dfs_unwrapper(getattr(item, key))
          for key in item.model_fields_set
        }
      else:
        return item
    inputs = [
      dfs_unwrapper(getattr(item,sanitize_parameter_names(P["parameter_name"])))
      for P in self.parameters
    ]
    fn_index = next(
      (i for i, d in self.app.fns.items() if d.api_name == self.api_name[1:]), # ignore first "/"
      None,
    )
    processed_input = self.app.serialize_data(fn_index, inputs)
    fn = self.app.fns[fn_index]
    outputs = gr_client_utils.synchronize_async(
      self.app.process_api,
      block_fn=fn,
      inputs=processed_input,
      request=None,
      state={}
    )
    outputs = outputs["data"]
    if fn.batch:
      outputs = [out[0] for out in outputs]
    outputs = self.app.deserialize_data(fn_index, outputs)
    processed_outputs = gr_utils.resolve_singleton(outputs)

    ONLY_1_OUTPUT = len(self.returns) == 1
    if ONLY_1_OUTPUT:
      processed_outputs = [processed_outputs]
    def normalize_JsonData(item):
      if isinstance(item, JsonData):
        return item.root
      return item
    processed_outputs = [*map(normalize_JsonData, processed_outputs)]

    if return_fomat=="list":
      return processed_outputs
    normalized_output = self.normalize_output(processed_outputs)

    return normalized_output

  def predict(self, item, return_fomat:Literal["list", "dict"]="dict"):
    if self.app:
      return self.predict_from_app(item, return_fomat)
    elif self.client:
      return self.predict_from_client(item, return_fomat)
    else:
      raise RuntimeError("should have one of app or client")

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

class LocalGraioApplication:
  app:gr.Blocks
  api_info:dict
  apis:dict[str, GradioAPI]

  def __init__(
    self,
    app:gr.Blocks,
  ):
    self.app = app
    self.api_info = app.get_api_info()
    self._prepare_api()

  def _prepare_api(self):
    self.__apis = {
      api_name:GradioAPI(
        api_name=api_name,
        config_dict=config_dict,
        app=self.app,
      )
      for api_name, config_dict in self.api_info["named_endpoints"].items()
    }

  @property
  def apis(self)->dict[str,GradioAPI]:
    return self.__apis

  def load_blocks(self, *TOIGNORE)->gr.Blocks:
    return self.app

class RemoteGradioApplication:
  src:str
  client_docuemnt:str
  client_info_dict:dict
  apis:dict[str, GradioAPI]

  def __init__(
    self,
    src:str,
    **gr_client_kwargs,
  ):
    client_kwargs = {
      "src":src,
      **gr_client_kwargs,
    }

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
        client=self.client,
      )
      for api_name, config_dict in self.client_info_dict["named_endpoints"].items()
    }

  @property
  def apis(self)->dict[str,GradioAPI]:
    return self.__apis

  def load_blocks(self, prefix:None|str=None)->gr.Blocks:
    client = self.client

    if client.app_version < version.Version("4.0.0b14"):
        raise GradioVersionIncompatibleError(
            f"Gradio version 4.x cannot load spaces with versions less than 4.x ({client.app_version})."
            "Please downgrade to version 3 to load this space."
        )

    predict_fns = []
    for fn_index, endpoint in client.endpoints.items():
      helper = client.new_helper(fn_index)
      if endpoint.backend_fn:
        predict_fns.append(endpoint.make_end_to_end_fn(helper))
      else:
        predict_fns.append(None)

    copied_config = deepcopy(client.config)
    if isinstance(prefix,str):  
      for d in copied_config["dependencies"]:
          d["api_name"] = f"{prefix[1:]}/"+d["api_name"]

    demo = gr.Blocks.from_config(copied_config, predict_fns, client.src)
    return demo