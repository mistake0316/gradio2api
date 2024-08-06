from typing import Any
from pydantic import BaseModel, model_validator
from .gr_fastapi import RemoteGradioAppRouter
from .utils.hash import add_key_and_verify as add_prefix_and_verify
from typing_extensions import Self
from fastapi import APIRouter

class AppConfig(BaseModel):
  uri:str
  prefix: str

  @model_validator(mode="after")
  def check_pefix(self)->Self:
    add_prefix_and_verify(self.prefix)
    return self

class Aggregator(APIRouter):
  config_list : list[AppConfig | dict]
  graido_app_routers: dict[str, RemoteGradioAppRouter]

  def __init__(
      self,
      config_list:list[AppConfig|dict],
      *router_args,
      **router_kwargs,
    ):
    super().__init__(*router_args, **router_kwargs)
    self.graido_app_routers = dict()
    self.config_list = self._normalize_config_list(config_list)
    self.assign_apis()

  @classmethod
  def _normalize_config_list(cls, config_list:list[AppConfig|dict]):
    ret = []
    for config in config_list:
      if isinstance(config, dict):
        ret.append(AppConfig(**config))
      else:
        ret.append(config)
    return ret
  
  def assign_apis(self):
    self.graido_app_routers = dict()
    for item in self.config_list:
      if isinstance(item, dict):
        item = AppConfig(**item)

      uri = item.uri
      prefix = item.prefix
      
      router = self.graido_app_routers[prefix] = RemoteGradioAppRouter(
        uri,
        prefix=prefix
      )
      self.include_router(router)
