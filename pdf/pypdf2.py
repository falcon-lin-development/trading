import PyPDF2

# Specify the path to your PDF file
pdf_file_path = '1.pdf'
txt_file_path = '1.txt'

# Open the PDF file in binary read mode
with open(pdf_file_path, 'rb') as pdf_file_obj:
    # Initialize the PDF reader
    pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
    
    # Get the total number of pages in the PDF
    num_pages = len(pdf_reader.pages)
    
    # Open the text file in write mode to save extracted text
    with open(txt_file_path, 'w', encoding='utf-8') as file:
        # Loop through all pages in the PDF
        for page_num in range(num_pages):
            # Get a page object
            page_obj = pdf_reader.pages[page_num]
            
            # Extract text from the page
            text = page_obj.extract_text()
            
            # Write the extracted text to the text file
            file.write(text)
            file.write('\n')  # Optionally, add a newline character between pages
