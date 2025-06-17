import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import TFRRSAPI.AthleteTfrrs as tfr
from ocr_parser.parser import extract_text_from_image, parse_athletes_old

def find_data(school, name):
  athlete = tfr.Athlete(school, name)
  athlete_data = athlete.get_all_data()
  for sect in athlete_data:
    print(sect)
    for item in athlete_data[sect]:
      print(item)


def just_ret_data(school, name):
  athlete = tfr.Athlete(school, name)
  athlete_data = athlete.get_all_data()
  return athlete_data


def dict_to_string(data_dict):
  result = ""
  for key, value in data_dict.items():
    result += key + ':\n'
    for item in value:
      result += f"  - {item}\n"
  return result


def main():
  img_path = "test_images/first_sheet.jpg"
  text = extract_text_from_image(img_path)
  print(text)
  athletes = parse_athletes_old(text)
  return
  for athlete in athletes:
    name = athlete['name']
    school = athlete['school']
    print(name, "-", school)
    find_data(athlete['school'], athlete['name'])
    print('\n')

if __name__ == "__main__":
  # main()
  print(dict_to_string(just_ret_data("LSU", "Trenton Sandler")))