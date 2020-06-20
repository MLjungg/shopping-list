import os

def store_in_notes(title):
    script = 'osascript '

    body = "create_note.scpt " + title

    os.system(script + body)
