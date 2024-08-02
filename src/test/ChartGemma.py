from utils import gr_endpoint
uri = "ahmed-masry/ChartGemma"
gr_app = gr_endpoint.RemoteGradioApplication("ahmed-masry/ChartGemma")
api = gr_app.apis["/predict"]
api.config_dict
api.parameter_model.model_json_schema()
api.return_model.model_json_schema()