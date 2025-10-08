import sys
import os
# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_db
from app.models.database_templates import ConsultationTemplate

def main():
    db = next(get_db())
    print(f"Templates count: {db.query(ConsultationTemplate).count()}")
    
    for template in db.query(ConsultationTemplate).all():
        print(f"Template: {template.name}")
        print(f"  Description: {template.description}")
        print(f"  Tags: {[tag.name for tag in template.tags]}")
        print(f"  Stages count: {len(template.stages)}")
        for i, stage in enumerate(template.stages):
            print(f"    Stage {i+1}: {stage.name}")
            print(f"      Prompt template: {stage.prompt_template}")
            print(f"      System instructions: {stage.system_instructions}")
            print(f"      Expected outputs: {[output.name for output in stage.expected_outputs]}")
        print()

if __name__ == "__main__":
    main()