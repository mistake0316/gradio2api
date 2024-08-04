from fastapi import FastAPI, APIRouter
from .gr_application import RemoteGradioApplication as GRA, GradioAPI 
from .hash import make_hash

def register_api(
  api_path:str,
  api:GradioAPI,
  hook:FastAPI | APIRouter,
  tags = list[str] | None,
):

  input_model = api.parameter_model
  async def __call(item:input_model):
    return api.predict(item)

  hook.post(
    api_path,
    response_model=api.return_model,
    summary=str(api).replace("\n", "\n\n"),
    tags=tags
  )(__call)

def remote_gr_application_to_fastapi(
  uri:str,
  prefix:str | None = None,
  hook:FastAPI | APIRouter | None = None,
):
  if hook is None:
    hook = APIRouter()
  if prefix is None:
    prefix = "/"+make_hash(uri)
  assert prefix[0] == "/"
  
  gra = GRA(uri)
  
  for api_name, api in gra.apis.items():
    register_api(
      f"{prefix}{api_name}",
      api=api,
      hook=hook,
      tags =[uri]+(
        [prefix]
        if prefix else
        []
      )
    )
  return hook