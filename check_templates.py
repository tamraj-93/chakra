import os
import json

templates_dir = "/home/nilabh/Projects/chakra/backend/data/templates"

def check_templates():
    print(f"Looking for templates in: {templates_dir}")
    if not os.path.exists(templates_dir):
        print(f"Error: Templates directory does not exist: {templates_dir}")
        return
        
    print(f"Directory contents: {os.listdir(templates_dir)}")
    
    for filename in os.listdir(templates_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(templates_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    template_data = json.load(f)
                
                # Check if this is a healthcare template
                tags = template_data.get('tags', [])
                domain = template_data.get('domain', '').lower()
                
                print(f"Template {filename}: tags={tags}, domain={domain}")
                
                if 'healthcare' in tags or 'healthcare' in domain.lower():
                    print(f"Found healthcare template: {filename}")
                    # Print full template details
                    print(json.dumps({
                        'id': template_data.get('id', os.path.splitext(filename)[0]),
                        'name': template_data.get('name', 'Unnamed Template'),
                        'description': template_data.get('description', ''),
                        'domain': domain,
                        'tags': tags,
                        'filename': filename,
                        'file_path': filepath
                    }, indent=2))
            except Exception as e:
                print(f"Error loading template {filename}: {str(e)}")

if __name__ == "__main__":
    check_templates()