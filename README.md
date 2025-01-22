## Agent OO7

**Setup Instructions**

To use this solution locally, ensure you have either `llama.cpp` or `Ollama` running with a suitable model. For optimal performance, use a larger model, such as `qwen2.5:32b` or above.

**Deployment Steps**

1. Set up a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Update the code to configure the correct model and URL for your inference engine.

**Run the Solution**  
Execute the program with the following command:

```bash
python main.py [plan|tool|interactive|blog]
```

**Additional Configuration for Weather Tool**  
To fetch weather details using the tool, provide your OpenWeatherMap API key. Register for an API key at [OpenWeatherMap](https://openweathermap.org/api) and add it to the `current_weather` function in the code.

---

*Reference*  
Inspired tools implementation by [SwirlAI 's blog](https://www.newsletter.swirlai.com/p/building-ai-agents-from-scratch-part)
