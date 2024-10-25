from pandasai import SmartDataframe
from pandasai.llm.local_llm import LocalLLM
import pandas as pd

# Sample DataFrame
sales_by_country = pd.DataFrame({
    "country": ["United States", "United Kingdom", "France", "Germany", "Italy", "Spain", "Canada", "Australia", "Japan", "China"],
    "sales": [5000, 3200, 2900, 4100, 2300, 2100, 2500, 2600, 4500, 7000]
})

ollama_llm = LocalLLM(api_base="http://localhost:11434/v1", model="codellama")
df = SmartDataframe(sales_by_country, config={"llm": ollama_llm})

print(df.chat('Which are the top 5 countries by sales?'))
# Output: China, United States, Japan, Germany, Australia
