import pytesseract
from PIL import Image
import pdf2image

# Convert PDF to a list of images
# Specify the path to your PDF file
pdf_file_path = '1.pdf'
txt_file_path = '1.txt'

pages = pdf2image.convert_from_path(pdf_file_path)

# Iterate over each page/image in the PDF
extracted_text = ""
for page in pages:
    # Use pytesseract to do OCR on the image file
    text = pytesseract.image_to_string(page)
    extracted_text += text

# Now, extracted_text contains the OCR results
# You can print it or save it to a file
# print(extracted_text)
with open(txt_file_path, 'w', encoding='utf-8') as file:
    file.write(extracted_text)