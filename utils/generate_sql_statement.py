import json

from common import FEEDBACK_IDS_FILE


def insert_data(ids, output_file):
    with open(output_file, 'w') as f:
        for nb in ids:
            f.write(f"INSERT INTO notebooks (name) VALUES ('{nb}');\n")
            for exercise in ids[nb]:
                cellId = exercise['cellId']
                position = exercise['position']
                f.write(f"""
                    INSERT INTO exercise (cell_id, position, notebook_id)
                    VALUES ('{cellId}', '{position}', (SELECT id FROM notebooks WHERE name = '{nb}'));
                    \n""")

# setup_tables()
with open(FEEDBACK_IDS_FILE, 'r') as f:
    data = json.load(f)
    insert_data(data, "feedback_ids.sql")
