import os
from lxml import etree
import openpyxl

def find_reqif_attribute_values(file_path: str, keyword: str):
    """
    Parses a ReqIF file, searches for a keyword in reqif-xhtml:object sections,
    and saves corresponding ATTRIBUTE-VALUE-STRING values to an Excel file.

    Args:
        file_path (str): The file path of the ReqIF XML file.
        keyword (str): The keyword to search for within the reqif-xhtml:object sections.
    """
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'")
        return

    # Define the namespaces used in the ReqIF file
    # This is crucial for correctly parsing the XML tags with prefixes.
    ns = {
        'reqif-xhtml': 'http://www.w3.org/1999/xhtml',
        'reqif': 'http://www.omg.org/spec/ReqIF/20110401/reqif.xsd'
    }

    try:
        # Create an XML parser and parse the file
        parser = etree.XMLParser(recover=True)
        tree = etree.parse(file_path, parser)
        root = tree.getroot()

        # List to store the extracted values
        extracted_values = []

        # Find all ATTRIBUTE-VALUE-XHTML elements
        xhtml_values = root.findall('.//reqif:ATTRIBUTE-VALUE-XHTML', namespaces=ns)
        
        # Loop through each ATTRIBUTE-VALUE-XHTML element
        for xhtml_val in xhtml_values:
            # Check for reqif-xhtml:object elements within the current element
            object_tag = xhtml_val.find('.//reqif-xhtml:object', namespaces=ns)
            
            # If a reqif-xhtml:object is found and its data attribute contains the keyword
            if object_tag is not None and keyword in object_tag.get('data', ''):
                # Find the sibling ATTRIBUTE-VALUE-STRING element.
                # The ATTRIBUTE-VALUE-STRING is typically a sibling of ATTRIBUTE-VALUE-XHTML
                # inside a parent tag like SPEC-OBJECT or a similar container.
                parent = xhtml_val.getparent()
                if parent is not None:
                    string_val = parent.find('./reqif:ATTRIBUTE-VALUE-STRING', namespaces=ns)
                    
                    if string_val is not None:
                        # Extract the THE-VALUE attribute
                        the_value = string_val.get('THE-VALUE')
                        if the_value:
                            extracted_values.append(the_value)

        # Handle the case where no values were found
        if not extracted_values:
            print(f"No '{keyword}' found in reqif-xhtml:object sections, so no Excel file was created.")
            return

        # Create a new Excel workbook and add a worksheet
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Extracted ReqIF Data"
        
        # Write the header to the first row
        sheet['A1'] = "Attribute Value"

        # Write the extracted values to the first column
        for index, value in enumerate(extracted_values, start=2):
            sheet[f'A{index}'] = value

        # Save the Excel file
        output_file = 'extracted_reqif_data.xlsx'
        workbook.save(output_file)
        
        # Get the absolute path of the saved file
        output_path = os.path.abspath(output_file)
        print(f"Successfully extracted {len(extracted_values)} values and saved them to '{output_file}' at '{output_path}'.")
        print(f"File is saved at:' '{output_path}'.")

    except Exception as e:
        print(f"An error occurred: {e}")