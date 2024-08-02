from gradio_client import Client, handle_file
from utils.model_builder import configs_list_to_model, PartParameter, PartReturn
from pydantic import BaseModel
from typing_extensions import Any

url = "http://10.119.55.27:9529/"

c = Client(url)
D = c.view_api(return_format="dict")["named_endpoints"]

models = dict()

for endpoint_name, setting in D.items():
  parameters_configs = [
    PartParameter(**p)
    for p in setting["parameters"]
  ]
  returns_configs = [
    PartReturn(**r)
    for r in setting["returns"]
  ]

  normalized_endpoint_name = endpoint_name.replace("/", "_")
  if normalized_endpoint_name[0] == "_":
    normalized_endpoint_name = normalized_endpoint_name[1:]
  
  parameters_model = configs_list_to_model(
    parameters_configs,
    model_name=f"{normalized_endpoint_name}_parameters"
  )
  returns_model = configs_list_to_model(
    returns_configs,
    model_name=f"{normalized_endpoint_name}_returns"
  )

  models[endpoint_name] = {
    "parameters": parameters_model,
    "returns": returns_model,
  }

from fastapi import FastAPI
app = FastAPI()

VP = models["/voice_activity_detection"]["parameters"]
VR = models["/voice_activity_detection"]["returns"]

print(VR.model_json_schema())
@app.post(
  "/voice_activity_detection",
  response_model=VR,
)
def voice_activity_detection(item:VP):
  print(item.model_dump())
  audio = handle_file(item.model_dump()["audio"])
  return {
    "segments":c.predict(
      audio=audio,
      api_name="/voice_activity_detection"
    )
  }

