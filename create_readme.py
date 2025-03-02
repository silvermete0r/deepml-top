import os
import datetime

README_FILE = "README.md"
README_TEMPLATE = "README_template.md"

def create_readme_if_not_exists():
    if not os.path.exists(README_FILE):
        try:
            with open(README_TEMPLATE, 'r', encoding='utf-8') as template_file:
                template_content = template_file.read()
            
            # Replace placeholder with current date
            today = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            readme_content = template_content.replace('{update_date}', today)
            
            with open(README_FILE, 'w', encoding='utf-8') as readme_file:
                readme_file.write(readme_content)
            
            print(f"Created {README_FILE} from template")
            return True
        except Exception as e:
            print(f"Error creating README file: {e}")
            return False
    return True

if __name__ == "__main__":
    create_readme_if_not_exists()
