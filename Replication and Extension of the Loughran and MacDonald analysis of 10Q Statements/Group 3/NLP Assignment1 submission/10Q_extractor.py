import os
import glob
import sec_parser as sp

# Define the directory containing the downloaded 10-Q HTML files
input_dir = 'downloaded_10Qs'

# Define the output directory for saving the extracted text
output_dir = 'sec_parser_10Q_txt'
os.makedirs(output_dir, exist_ok=True)  # Create the output directory if it doesn't exist

# Function to extract all text from the HTML content using sec_parser and save it level by level
def extract_text_level_by_level(tree, output_file_path):
    """
    Traverse the tree level by level, extract text from each element, save it to a file, and print it.

    Parameters:
        tree (SemanticTree): A semantic tree built from the 10-Q filing.
        output_file_path (str): Path to the output text file where extracted content will be saved.
    """
    # Open the output text file for writing
    with open(output_file_path, 'w', encoding='utf-8') as file:
        # Traverse the tree nodes level by level
        for node in tree.nodes:
            # Check if the node is a TitleElement or any other relevant element
            if isinstance(node.semantic_element, sp.TitleElement):
                # Render the TitleElement text and write it to the file and print it
                title_text = node.semantic_element.text
                file.write(f"Title: {title_text}\n")
                # print(f"Title: {title_text}\n")  # Print the title to the terminal

            # Check for SupplementaryText (or other nested elements) and render them
            for child in node.children:
                if hasattr(child.semantic_element, 'text'):
                    element_text = child.semantic_element.text
                    file.write(f"{element_text}\n")
                    # print(f"{element_text}\n")  # Print the element text to the terminal

            file.write("\n")  # Add spacing between sections for readability
            # print("\n")  # Print spacing between sections on the terminal

    print(f"Extracted text saved to {output_file_path}")

# Get all HTML files in the input directory
html_files = glob.glob(os.path.join(input_dir, '*.html'))

# Process each HTML file in the folder
for html_file in html_files:
    # Read the content of the HTML file
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML content into semantic elements and build a tree
    elements = sp.Edgar10QParser().parse(html_content)
    tree = sp.TreeBuilder().build(elements)

    # Get the base name of the file to create a corresponding output text file
    base_name = os.path.basename(html_file)
    file_name, _ = os.path.splitext(base_name)

    # Define the output file path
    output_text_file = os.path.join(output_dir, f"{file_name}_extracted.txt")

    # Extract text level by level, print it to the terminal, and save it to a text file
    extract_text_level_by_level(tree, output_text_file)
