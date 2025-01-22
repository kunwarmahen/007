## Agent OO7

To play with locally you need to have llama.cpp or ollama running locally with a model (preferally bigger model like or above qwen2.5:32b)

To deploy:

python -m venv .venv
source.venv/bin/activate
pip install -r requirements.txt

Updated the code to use correct model and URL for your inference engine.

To run:
python main.py [plan|tool|interactive|blog]

To use tool to get weather detail, you need to provide your OpenWeatherMap (https://openweathermap.org/api) API key in the `current_weather` function.
