from fastapi import APIRouter
from .gr_application import RemoteGradioApplication as RGA, LocalGraioApplication as LGA 
from gradio import Blocks
import gradio as gr

class GradioAPIRouter(APIRouter):
  gradio_application: RGA | LGA

  def __init__(
    self,
    gradio_application: RGA | LGA,
    *router_args,
    **router_kwargs,
  ):
    super().__init__(*router_args, **router_kwargs)
    self.gradio_application = gradio_application
    self._preprocess()

  def load_gr_blocks(self, prefix:None|str)->Blocks:
    return self.gradio_application.load_blocks(prefix)

  def _preprocess(self):
    for api_name in self.gradio_application.apis.keys():
      self._register_gradio_api(
        api_name=api_name,
      )

  def _register_gradio_api(
    self,
    api_name:str,
    tags:list[str] | None = [],
  ):
    api = self.gradio_application.apis[api_name]
    request_model = api.parameter_model
    response_model = api.return_model

    async def __call_api(item):
      return api(item)
    __call_api.__annotations__ = {
      "item":request_model,
      "return":response_model,
    }

    if tags is None:
      tags = []

    self.post(
      api_name,
      tags=tags
    )(__call_api)

class LocalGradioAppRouter(GradioAPIRouter):
  gradio_application: LGA
  def __init__(
      self,
      app:Blocks,
      *router_args,
      **router_kwargs,
  ):
    super().__init__(
      gradio_application=LGA(app),
      *router_args,
      **router_kwargs
    )

class RemoteGradioAppRouter(GradioAPIRouter):
  gradio_uri:str

  def __init__(
      self,
      gradio_uri:str,
      *router_args,
      **router_kwargs,
  ):
    super().__init__(
      gradio_application=RGA(src=gradio_uri),
      *router_args,
      **router_kwargs
    )
    self.gradio_uri = gradio_uri
