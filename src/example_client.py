from fastapi import FastAPI
from gradio2api.clients_aggregator import Aggregator as ClientAggreator

remote_servers_list = [
  {
    "uri":"tonyassi/voice-clone",
    "prefix":"/voice-clone"
  },
  {
    "uri":"turboedit/turbo_edit",
    "prefix":"/turbo_edit"
  },
]
router = ClientAggreator(remote_servers_list)
app = FastAPI()
app.include_router(router)