from enum import Enum

class Button(Enum):
    BUTTON_TEXT_PROCEED = "Looks good, proceed!"
    BUTTON_TEXT_JOIN_DETAILS = "Tell me more about join"

def determine_buttons(vector_db, response):
    button_list = vector_db.search(response)
    button_names = set(map(lambda x: Button(x[0].page_content), button_list))
    button_names.add(Button.BUTTON_TEXT_PROCEED)
    return button_names

def string_to_button(text):
    return Button(text)