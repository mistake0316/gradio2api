from .models_parameters import TYPES as PARAMETER_TYPES
from .models_returns import TYPES as RETURN_TYPES

LOWER_PARAMETER_TYPES = {k.lower(): v for k, v in PARAMETER_TYPES.items()}
LOWER_RETURN_TYPES = {k.lower(): v for k, v in RETURN_TYPES.items()}