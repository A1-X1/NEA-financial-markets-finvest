import os

def map_project_structure(start_path='.'):
    print(f"Checking structure for: {os.path.abspath(start_path)}\n")
    
    # Files/folders to ignore to keep output clean
    ignore_list = {'.git', '__pycache__', '.vscode', '.idea'}

    for root, dirs, files in os.walk(start_path):
        # Filter out ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_list]
        
        # Calculate indentation level
        level = root.replace(start_path, '').count(os.sep)
        indent = ' ' * 4 * (level)
        
        # Print the current directory
        print(f"{indent}📂 {os.path.basename(root)}/")
        
        # Print the files in the directory
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            if f.endswith('.py'):
                print(f"{sub_indent}🐍 {f}")
            elif f == '__init__.py':
                print(f"{sub_indent}⭐ {f} (PACKAGE MARKER)")
            else:
                print(f"{sub_indent}📄 {f}")

if __name__ == "__main__":
    map_project_structure()