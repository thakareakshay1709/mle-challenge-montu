# Training examples in the format [{"text": str, "redacted_text": str}]
import json
import os

def load_file():
    data_path = "data/pii_data.json"
    if os.path.exists(data_path):
        with open(data_path) as file:
            data = json.load(file)
    else:
        data = None
        raise FileNotFoundError(data_path)
    return data

def load_data():
    return {"training_data": load_file()}


# TRAINING_DATA = [
#     {
#         "text": "Maria Garcia is the new CEO.",
#         "redacted_text": "[NAME] is the new CEO."
#     },
#     {
#         "text": "The company is located at 202 Grenfell Street, Adelaide, SA 5000.",
#         "redacted_text": "The company is located at [ADDRESS]."
#     },
#     {
#         "text": "Please contact Sarah Thompson at sarah.thompson@company.com.au or 0422 111 222 to schedule a meeting.",
#         "redacted_text": "Please contact [NAME] at [EMAIL] or [PHONE_NUMBER] to schedule a meeting."
#     },
#     {
#         "text": "The company headquarters are located at 123 Main Street, Sydney, NSW 2000.",
#         "redacted_text": "The company headquarters are located at [ADDRESS]."
#     },
#     {
#         "text": "Contact us at support@company.com or call (02) 9876 5432 for assistance.",
#         "redacted_text": "Contact us at [EMAIL] or call [PHONE_NUMBER] for assistance."
#     },
#     {
#         "text": "John Smith works at Acme Corporation in New York.",
#         "redacted_text": "[NAME] works at [ORGANIZATION] in [ADDRESS]."
#     },
#     {
#         "text": "Send your documents to legal@acme.com or visit our office at 456 Business Ave.",
#         "redacted_text": "Send your documents to [EMAIL] or visit our office at [ADDRESS]."
#     },
#     {
#         "text": "For more information, contact marketing@company.org or visit 789 Tech Road.",
#         "redacted_text": "For more information, contact [EMAIL] or visit [ADDRESS]."
#     },
#     {
#         "text": "Our CEO is Michael Johnson and he can be reached at ceo@company.com.",
#         "redacted_text": "Our CEO is [NAME] and he can be reached at [EMAIL]."
#     },
#     {
#         "text": "The meeting is scheduled at 999 Innovation Drive, Silicon Valley.",
#         "redacted_text": "The meeting is scheduled at [ADDRESS]."
#     }
# ]