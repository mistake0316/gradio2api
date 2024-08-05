from gradio_client_fastapi.utils.gr_fastapi import remote_gr_application_to_fastapi
from fastapi import FastAPI

remote_servers = [
  {
    "uri":"ahmed-masry/ChartGemma",
    "prefix":"/ChartGemma",
  },
  {
    "uri":"zheyangqin/VADER",
    "prefix":"/VADER",
  },
]
app = FastAPI()

for item in remote_servers:
  uri = item.pop("uri")
  prefix = item.pop("prefix")
  remote_gr_application_to_fastapi(
    uri=uri,
    prefix=prefix,
    hook=app,
  )

