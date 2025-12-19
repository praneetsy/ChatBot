import json
import csv
import ast

def extract_content(history_str):
    history_dict = json.loads(history_str)
    return history_dict
def convert_json_to_csv(input_file, output_file):
    # Read JSON data
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Prepare CSV data
    csv_data = []
    session_id_map = {}

    for i in range(0, len(data)):
        session_id = data[i]['SessionId']
        if session_id not in session_id_map:
            session_id_map[session_id] = [
                data[i]
            ]
        else:
            session_id_map[session_id].append(data[i])
    
    response = []
    for session_id in session_id_map:
        session_data = session_id_map[session_id]
        question_answer_map = {}
        for ele in session_data:
            history_data = extract_content(ele['History'])
            if history_data['type'] == 'human':
                if ele['QuestionGuid'] in question_answer_map:
                    question_answer_map[ele['QuestionGuid']]['question'] = history_data['data']['content']
                else:
                    question_answer_map[ele['QuestionGuid']] = {
                        'question': history_data['data']['content'],
                        'answer': "",
                        'agent_name': ele['AgentName']
                    }
            elif history_data['type'] == "ai":
                if ele['QuestionGuid'] in question_answer_map:
                    question_answer_map[ele['QuestionGuid']]['answer'] = history_data['data']['content']
                else:
                    question_answer_map[ele['QuestionGuid']] = {
                        'question': "",
                        'answer': history_data['data']['content'],
                        'agent_name': ele['AgentName']
                    }
        for question_guid in question_answer_map:
            response.append({
                'SessionId': session_id,
                'QuestionGuid': question_guid,
                'ResponseGuid': question_answer_map[question_guid]['agent_name'],
                'EpochTime': ele['EpochTime'],
                'Question': question_answer_map[question_guid]['question'],
                'Answer': question_answer_map[question_guid]['answer']
            })
    csv_data.extend(response)



    # Write CSV file
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
        writer.writeheader()
        writer.writerows(csv_data)

# Usage
input_file = 'input.json'
output_file = 'output.csv'
convert_json_to_csv(input_file, output_file)
print(f"Conversion complete. CSV file saved as {output_file}")