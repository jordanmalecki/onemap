import os
import pyperclip
import json
import csv

def list_files(startpath):
    tree_output = "tree:\n\"\"\"\n"
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        level = root.replace(startpath, '').count(os.sep)
        indent = '│   ' * (level - 1) + '├── ' if level > 0 else ''
        tree_output += '{}{}/\n'.format(indent, os.path.basename(root))
        subindent = '│   ' * level + '├── '
        for f in files:
            if not (f.startswith('.') or 
                    f.endswith(('.md', '.html', '.jpg', '.png')) or 
                    f == 'gpt.py'):
                tree_output += '{}{}\n'.format(subindent, f)
    tree_output += "\"\"\"\n\n"
    return tree_output

def file_contents(startpath):
    contents_output = ""
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for f in files:
            if not (f.startswith('.') or 
                    f.endswith(('.md', '.html', '.jpg', '.png')) or 
                    f == 'gpt.py'):
                filepath = os.path.join(root, f)
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                    if f.endswith('.json'):
                        data = json.load(file)
                        content = json.dumps(data, indent=4)
                        # Assuming you want the first object or key in the JSON
                        first_key = list(data.keys())[0]
                        content = json.dumps({first_key: data[first_key]}, indent=4)
                    elif f.endswith('.csv'):
                        reader = csv.reader(file)
                        rows = list(reader)
                        # Assuming you want the header and the first row of the CSV
                        content = "\n".join([",".join(row) for row in rows[:2]])
                    else:
                        content = file.read()
                    contents_output += './{}:\n\"\"\"\n{}\n\"\"\"\n\n'.format(filepath.replace(startpath + '/', ''), content)
    return contents_output

if __name__ == "__main__":
    startpath = '.'  # Current directory
    output = list_files(startpath)
    output += file_contents(startpath)
    print(output)
    
    # Copy the output to clipboard
    pyperclip.copy(output)
