import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import requests
import ast
import openai
import TFRRSAPI.AthleteTfrrs as tfr
from ocr_parser.parser import extract_text_from_image, parse_athletes_old



def just_ret_data(school, name):
  athlete = tfr.Athlete(school, name)
  athlete_data = athlete.get_all_data()
  athlete_data['Name'] = name
  return athlete_data


def scan_no_data(img_path):
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


def ai_insights(name, prs):
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


def scan_athletes_ai(img_path):
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


def test_script_1():
  img_path = "test_images/first_sheet.jpg"
  text = extract_text_from_image(img_path)
  athletes = parse_athletes_old(text)
  for athlete in athletes:
    name = athlete['name']
    school = athlete['school']
    print(name, "-", school)
    find_data(athlete['school'], athlete['name'])
    print('\n')


def main():
  # start = time.time()

  # print(scan_no_data("test_images/first_sheet.jpg"))
  # print(extract_text_from_image("test_images/test100.jpg"))
  # print((ask_llama("Tell me a short poem")))
  print(just_ret_data("school", "Trenton Sandler"))
  # print(scan_athletes_ai("test_images/test100.jpg"))
  # data = scan_athletes_ai("test_images/test100.jpg")

  # end = time.time()
  # print(f"Elapsed time: {end - start:.4f} seconds")
  print("Done")

if __name__ == "__main__":
  main()

  

