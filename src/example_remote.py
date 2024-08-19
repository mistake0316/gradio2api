from gradio2api import create_gradio2api

remote_servers_list = [
  {
    "uri":"SinDarSoup/TheWorld",
    "prefix":"/space",
  },
  {
    "uri":"https://sindarsoup-theworld.hf.space",
    "prefix":"/iframe",
  },
]
app = create_gradio2api(
  servers=remote_servers_list
)

def health_check():
    return {"status": "OK", "message": "The taq client app is running"}  

app.get("/health")(health_check)
