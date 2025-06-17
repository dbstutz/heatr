from ocr_parser.parser import extract_text_from_image, parse_athletes_old, parse_text

img_path = "test_images/first_sheet.jpg"
text = extract_text_from_image(img_path)

print("\nOCR Result:\n", text)

'''
print("old try")
athletes = parse_athletes_old(text)
print("\nExtracted Athletes:")
for athlete in athletes:
    print(f"{athlete['name']} - {athlete['school']}")
'''

print("new try")
athletes = parse_text(text)
for athlete in athletes:
    print(f"{athlete[0]} - {athlete[1]}")