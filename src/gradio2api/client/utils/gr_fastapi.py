from fastapi import APIRouter
from .gr_application import RemoteGradioApplication as GRA, GradioAPI 

class GradioAppRouter(APIRouter):
  gradio_uri:str
  gradio_application:GRA

  def __init__(
      self,
      gradio_uri:str,
      *router_args,
      **router_kwargs,
  ):
    super().__init__(*router_args, **router_kwargs)
    self.gradio_uri = gradio_uri
    self.gradio_application = GRA(gradio_uri)
    self.preprocess()

  def preprocess(self):
    for api_name in self.gradio_application.apis.keys():
      self.register_gradio_api(
        api_name=api_name,
        tags=[api_name]
      )

  def register_gradio_api(
    self,
    api_name:str,
    tags:list[str] | None = [],
  ):
    api = self.gradio_application.apis[api_name]
    request_model = api.parameter_model
    response_model = api.return_model

    async def call_api(item):
      return api(item)
    call_api.__annotations__ = {
      "item":request_model,
      "return":response_model,
    }

    if tags is None:
      tags = []
    
    self.post(
      api_name,
      tags=tags
    )(call_api)