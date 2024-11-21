import ast
import json

def extract_json(text):
    stack = []
    json_start = None

    for i, char in enumerate(text):
        if char == '{':
            if not stack:
                json_start = i
            stack.append(char)
        elif char == '}':
            try:
                stack.pop()
            except:
                pass
            if not stack:
                json_end = i + 1
                json_str = text[json_start:json_end]
                try:
                    json_data = json.loads(json_str)
                    
                    return json_data
                except json.JSONDecodeError:
                    try:
                        json_data = ast.literal_eval(json_str)
                        return json_data
                    except:
                        try:
                            if not json_str.endswith('}'):
                                json_str += '}'
                            json_data = json.loads(json_str.replace("'", '"'))
                            return json_data
                        except:
                            pass
                    pass
    return None

def handle_md_json(text):
    if text.startswith('```') and text.endswith('```'):
        braces_start_pos = text.find('{')
        list_start_pos = text.find('[')
        # check if the braces are present
        if braces_start_pos != -1:
            braces_end_pos = text.rfind('}')
            return text[braces_start_pos:braces_end_pos+1]
        # check if the list is present
        elif list_start_pos != -1:
            list_end_pos = text.rfind(']')
            return text[list_start_pos:list_end_pos+1]
    return None