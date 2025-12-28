# Ultra simple model control with just one variable
is_model_on = 0  # 0 = off, 1 = on

def turn_on():
    global is_model_on
    is_model_on = 1
    return "Model turned ON"

def turn_off():
    global is_model_on
    is_model_on = 0
    return "Model turned OFF"

def get_status():
    return is_model_on