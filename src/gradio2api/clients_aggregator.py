from typing import Any
from pydantic import BaseModel, model_validator
from .gr_fastapi import RemoteGradioAppRouter
from .utils.hash import add_key_and_verify as add_prefix_and_verify
from typing_extensions import Self
from typing import Optional
from fastapi import APIRouter, FastAPI
import gradio as gr
import traceback
import pandas as pd
import json

class AppConfig(BaseModel):
  uri:str
  prefix: str

  # @model_validator(mode="after")
  # def check_pefix(self)->Self:
  #   add_prefix_and_verify(self.prefix)
  #   return self

class Status(BaseModel):
  api_success: bool
  gui_success: bool
  api_building_error_msg: Optional[str] = None
  gui_building_error_msg: Optional[str] = None

class PostAppConfig(AppConfig):
  status:Status
  api_names: Optional[list[str]] = None
  num_of_apis:Optional[int] = None

class Info(BaseModel):
  info: list[PostAppConfig] = []

class Aggregator(APIRouter):
  config_list : list[AppConfig | dict]
  graido_app_routers: dict[str, list[RemoteGradioAppRouter]]
  gradio_guis: dict[str, list[gr.Blocks]]
  error_allowed_api:bool
  error_allowed_gui:bool
  info: Info

  def __init__(
      self,
      config_list:list[AppConfig|dict],
      error_allowed_api:bool=False,
      error_allowed_gui:bool=True, # TODO: design for customize package
      *router_args,
      **router_kwargs,
    ):
    super().__init__(*router_args, **router_kwargs)
    self.get("/info")(self.get_info)

    self.config_list = []
    self.graido_app_routers = dict()
    self.gradio_guis = dict()
    self.info = Info()
    self.error_allowed_api = error_allowed_api
    self.error_allowed_gui = error_allowed_gui

    self.assign_from_config_list(config_list)

  def get_info(self)->Info:
    return self.info

  @classmethod
  def _normalize_config(cls, config:list[AppConfig|dict]):
    if isinstance(config, AppConfig):
      return config
    return AppConfig(**config)

  def assign_from_config(self, config:AppConfig|dict):
    config = self._normalize_config(config)
    self.config_list.append(config)

    uri = config.uri
    prefix = config.prefix
    api_building_error_msg = None
    gui_building_error_msg = None
    api_names = []

    try:
      router = RemoteGradioAppRouter(
        gradio_uri=uri,
        prefix=prefix,
      )
      api_names = list(router.gradio_application.apis.keys())

      if prefix not in self.graido_app_routers:
          self.graido_app_routers[prefix] = []

      self.graido_app_routers[prefix].append(router)
      self.include_router(router)
    except Exception as e:
      if self.error_allowed_api:
        api_building_error_msg = traceback.format_exc()
        print("[SKIP ERROR]",e)
      else:
        raise e

    try:
      gui = router.load_gr_blocks(
        prefix=prefix,
      )
      if prefix not in self.gradio_guis:
          self.gradio_guis[prefix] = []
      
      self.gradio_guis[prefix].append(gui)
    except Exception as e:
      if self.error_allowed_gui:
        gui_building_error_msg = traceback.format_exc()
        print("[SKIP ERROR]",e)
      else:
        raise e

    self.info.info.append(
      PostAppConfig(
        uri=uri,
        prefix=prefix,
        status=Status(
          api_success=api_building_error_msg is None,
          api_building_error_msg=api_building_error_msg,
          gui_success=gui_building_error_msg is None,
          gui_building_error_msg=gui_building_error_msg,
        ),
        api_names=api_names,
        num_of_apis=len(api_names),
      )
    )

  def assign_from_config_list(self, config_list):
    for config in config_list:
      self.assign_from_config(config)

  @property
  def grand_gr_app(self)->gr.Blocks:
    app = gr.TabbedInterface(
      [self.gr_info, self.gr_app],
      ["Information", "Application"],
    )
    return app
  
  @property
  def gr_app(self)->gr.TabbedInterface:
    tabs = []
    names = []
    for prefix, guis in self.gradio_guis.items():
      if len(guis) == 0:
        continue

      names.append(prefix)
      if len(guis) == 1:
        tabs.append(guis[0])
        continue

      _local_tabs = []
      _local_names = []
      for idx, gui in enumerate(guis):
        _local_tabs.append(gui)
        _local_names.append(f"{idx:3d}")
      tabs.append(
        gr.TabbedInterface(
          _local_tabs,
          _local_names
        )
      )

    return gr.TabbedInterface(tabs,names)
  
  @property
  def gr_info(self)->gr.DataFrame:
    
    info_list = self.get_info().info
    df_data = [
      {
        "prefix":I.prefix,
        "uri":I.uri,
        "API Loaded": {
          True:"Success",
          False:"Fail",
        }[I.status.api_success],
        "GUI Loaded": {
          True:"Success",
          False:"Fail",
        }[I.status.gui_success],
        "APIS":f"""({I.num_of_apis}) [{", ".join(I.api_names)}]""",
      }
      for I in info_list
    ]

    df = pd.DataFrame(df_data)
    gr_df = gr.DataFrame(df)
    return gr_df

from typing import TypedDict
class Server(TypedDict):
  uri: str
  prefix: str


def create_gradio2api(
  servers: list[Server],
  *,
  gradio_client_config_path :str = None,
  error_allowed=True,
):

  remote_servers_config_list = []
  for S in servers:
    remote_servers_config_list.append(S)

    J = {}
    if gradio_client_config_path:
      J = json.load(open(gradio_client_config_path,"r"))

    remote_servers_config_list = [
      {
        **J,
        **orginal_config,
      }
      for orginal_config in remote_servers_config_list
    ]

  aggregator_router = Aggregator(
    remote_servers_config_list,
    error_allowed_api=error_allowed
  )
  app = FastAPI()
  app.include_router(aggregator_router)
  app = gr.mount_gradio_app(
    app,
    aggregator_router.grand_gr_app,
    "/gui"
  )
  return app