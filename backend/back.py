import ast
import AthleticAPI.AthleticNetAthlete as anet
from dotenv import load_dotenv
from ocr_parser.parser import extract_text_from_image, parse_athletes_old
from openai import OpenAI
import os
import requests
import sys
import TFRRSAPI.TFRRSAthlete as tfr
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
  )


def fetch_athlete_data(school, name):
  athlete = tfr.Athlete(school, name)
  athlete_data = athlete.get_all_data()
  athlete_data['Name'] = name
  return athlete_data


def scan_regex(img_path):
  text = extract_text_from_image(img_path)
  athletes = parse_athletes_old(text)
  heat_data = []
  for athlete in athletes:
    name = athlete['name']
    school = athlete['school']
    heat_data.append({"name": name, "school": school})
  return heat_data


def ask_llama(prompt):
  response = requests.post(
      "http://localhost:11434/api/generate",
      json={
          "model": "llama3",
          "prompt": prompt,
          "stream": False
    }
  )
  data = response.json()
  return(data['response'])


def insights_llama(name, prs):
  prompt = f"""
    Give a brief summary on this athlete, {name} based off of their personal record data.
    This will be used by a competitor for racing strategy.
    For example, on an athlete with a stronger 800m time than 1500m time, you might say:
    "{name} is a strong runner but times get less impressive as distances get longer. Would most likely prosper in a sit-and-kick race."
    Return ONLY the insight, no other text or heading.
    Here is their PR data:
    {str(prs)}
  """
  return ask_llama(prompt)


def scan_athletes_llama(img_path):
  ocr_text = extract_text_from_image(img_path)
  
  prompt_athlete = """
  You will receive raw OCR text. It includes a list of athlete names.

  Your task is to extract only the athlete names an output a formatted python list.

  Do NOT reorder anything.
  DO keep each athlete in the same position.
  DO NOT include anything besides the list itself.
  IGNORE random characters, numbers, or other text that is not for sure an athlete name even if it is next to it.
  DO NOT print introductory text, explanation, or headings.
  ONLY return a valid Python list of athletes.
  Output MUST look like this ONLY:
  ["Usain Bolt", "Lebron James", "Lionel Messi"...]

  If you are unsure, skip that entry — but never guess or hallucinate.

  Here is the text:
  """

  athlete_result = ask_llama(prompt_athlete + ocr_text)
  athlete_list = ast.literal_eval(athlete_result)

  prompt_school = f"""
  You will receive raw OCR text. It includes a list of {len(athlete_list)} school names, with possible duplicates.

  Your task is to extract only the school names an output a formatted python list.

  Do NOT reorder anything.
  DO keep each school in the same position, including duplicates.
  DO NOT include anything besides the list itself.
  DO NOT print introductory text, explanation, or headings.
  Look for a pattern, and ignore text that could be a school name if it is out of the pattern.
  ONLY return a valid Python list of {len(athlete_list)} schools.
  Output MUST look like this:
  ["Ole Miss", "Missouri", "Ole Miss"...]

  If you are unsure, skip that entry — but never guess or hallucinate.

  Here is the text:
  """
  school_result = ask_llama(prompt_school + ocr_text)
  school_list = ast.literal_eval(school_result)

  pairs = []
  for i in range(len(athlete_list)):
    school = school_list[i]
    name = athlete_list[i]
    pairs.append({"name": name, "school": school})
  return pairs


def parse_gpt(input):
  
  completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "developer", "content": "You are a helpful assistant. Extract athlete names and schools from text. Return a Python-style list of (name, school) tuples, but output it as plain text — no markdown code blocks, no syntax highlighting, and no python label."},
        {
            "role": "user",
            "content": f"""
            Extract athlete names and schools.
            Return ONLY a python list of tuples like: ("Name", "School")
            Text:
            {input}
            """,
        },
    ],
  )

  return(completion.choices[0].message.content)


def scan_athletes_gpt(img_path):
  ocr_text = extract_text_from_image(img_path)
  gpt_struct = parse_gpt(ocr_text)
  tuplist = ast.literal_eval(gpt_struct)
  pairs = []
  for tup in tuplist:
    school = tup[1]
    name = tup[0]
    pairs.append({"name": name, "school": school})
  return pairs


def insights_gpt(name, prs):
  completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "developer", "content": "You are a track and field expert. Provide insights on a athlete based on their personal record data."},
        {
            "role": "user",
            "content": f"""
              Give a brief summary on this athlete, {name} based off of their personal record data.
              This will be used by a competitor for racing strategy.
              For example, on an athlete with a stronger 800m time than 1500m time, you might say:
              "{name} is a strong runner but times get less impressive as distances get longer. Would most likely prosper in a sit-and-kick race."
              Return ONLY the insight, no other text or heading.
              Here is their PR data:
              {str(prs)}
            """,
        },
    ],
  )

  return(completion.choices[0].message.content)


def main():
  # start = time.time()

  # print(scan_no_data("test_images/first_sheet.jpg"))
  # print(extract_text_from_image("test_images/test100.jpg"))
  # print(scan_athletes_gpt("test_images/goofy.PNG"))

  # end = time.time()
  # print(f"Elapsed time: {end - start:.4f} seconds")
  pass


if __name__ == "__main__":
  main()
  boyA = anet.Athlete("LSU", "Trenton Sandler")
  boyT = tfr.Athlete("LSU", "Trenton Sandler")
  print(boyA.get_all_data())
  print(boyT.get_all_data())

  

