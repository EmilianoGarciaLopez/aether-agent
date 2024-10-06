# %%
import json
import sys
import re
import pprint
from IPython.display import display, Markdown, Image
import base64


def messages_to_html(messages, output_file='messages.html'):
    html_content = '<html><body>\n'
    for message in messages:
        role = message.get('role', 'unknown')
        name = message.get('name', '')
        content_items = message.get('content', [])
        header = f"<h2>Role: {role}"
        if name:
            header += f", Name: {name}"
        header += "</h2>\n"
        html_content += header

        for item in content_items:
            item_type = item.get('type', 'text')
            if item_type == 'text':
                text_content = item.get('text', '').replace('\n', '<br>')
                html_content += f"<p>{text_content}</p>\n"
            elif item_type == 'image_url':
                url = item.get('image_url', {}).get('url', '')
                html_content += f'<img src="{url}" alt="Image">\n'
        html_content += '<hr>\n'
    html_content += '</body></html>'

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Messages have been exported to {output_file}")


def visualize_messages_markdown(messages):
    for idx, message in enumerate(messages, 1):
        role = message.get('role', 'unknown')
        name = message.get('name', '')
        content_items = message.get('content', [])
        header = f"## Message {idx}: Role: {role}"
        if name:
            header += f", Name: {name}"
        print(header)
        print()

        text_entries = [item for item in content_items if item.get('type') == 'text']
        image_entries = [item for item in content_items if item.get('type') == 'image_url']

        # Handle text entries
        for i, item in enumerate(text_entries, 1):
            text_content = item.get('text', '')
            # Pre-process the text to avoid backslashes in f-string expressions
            formatted_text = text_content.strip().replace('\n', '\n> ')
            print(f"### Text Entry {i}:\n")
            print(f"> {formatted_text}\n")

        # Handle image entries
        for i, item in enumerate(image_entries, 1):
            url = item.get('image_url', {}).get('url', '')
            print(f"### Image Entry {i}:\n")
            print(f"![Image {i}]({url})\n")

        print('---')  # Separator between messages


def visualize_messages_jupyter(messages, img_width=600):
    for idx, message in enumerate(messages, 1):
        role = message.get('role', 'unknown')
        name = message.get('name', '')
        content_items = message.get('content', [])
        text_entries = [item for item in content_items if item.get('type') == 'text']
        image_entries = [item for item in content_items if item.get('type') == 'image_url']
        
        # Message Header
        header = f"## Message {idx}: Role: {role}"
        if name:
            header += f", Name: {name}"
        display(Markdown(header))
        
        # Text Entries
        for i, item in enumerate(text_entries, 1):
            text_content = item.get('text', '')
            formatted_text = text_content.strip().replace('\n', '\n> ')
            display(Markdown(f"### Text Entry {i}:\n"))
            display(Markdown(f"> {formatted_text}\n"))
        
        # Image Entries
        for i, item in enumerate(image_entries, 1):
            url = item.get('image_url', {}).get('url', '')
            display(Markdown(f"### Image Entry {i}:\n"))
            if url.startswith('data:image/'):
                # Extract the base64 data
                header, base64_data = url.split(',', 1)
                img = Image(data=base64.b64decode(base64_data), width=img_width)
                display(img)
            else:
                # Display image from URL
                display(Markdown(f"![Image {i}]({url})\n"))
        
        display(Markdown('---'))


def shorten_base64_strings(obj):
    """
    Recursively traverse the object and shorten any Base64 strings to a maximum of 10 characters.
    """
    base64_pattern = re.compile(r'(data:[^;]+;base64,)([A-Za-z0-9+/=]+)')
    
    if isinstance(obj, dict):
        # Recursively process dictionary values
        return {k: shorten_base64_strings(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        # Recursively process list items
        return [shorten_base64_strings(item) for item in obj]
    elif isinstance(obj, str):
        # Shorten Base64 strings in the string
        def replacer(match):
            prefix = match.group(1)
            base64_str = match.group(2)
            # Shorten the Base64 string if it's longer than 10 characters
            if len(base64_str) > 10:
                base64_str = base64_str[:10]
            return prefix + base64_str
        return base64_pattern.sub(replacer, obj)
    else:
        # Return the object unchanged if it's not a dict, list, or string
        return obj

def shorten_base64_in_messages(messages):
    """
    Process a list of OpenAI messages and shorten all Base64 strings within them.
    """
    return [shorten_base64_strings(message) for message in messages]



def main():
    # Read from stdin
    # data = sys.stdin.read()
    with open('raw_messages.txt', 'r') as f:
        data = f.read()

    # Extract messages between <start_messages> and <end_messages>
    pattern = re.compile(r'<start_messages>(.*?)<end_messages>', re.DOTALL)
    matches = pattern.findall(data)

    if not matches:
        print("No messages found between <start_messages> and <end_messages> tags.")
        sys.exit(1)

    # Assuming there's only one messages block
    message_data = matches[0].strip()

    # Parse the JSON data directly
    try:
        messages = json.loads(message_data)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON data: {e}")
        sys.exit(1)

    # Verify that messages is a list
    if not isinstance(messages, list):
        print(f"Error: Expected messages to be a list but got {type(messages)}")
        sys.exit(1)

    # Optional: Validate each message
    for idx, message in enumerate(messages):
        if not isinstance(message, dict):
            print(f"Error: messages[{idx}] is not a dictionary. It is a {type(message)}")
            sys.exit(1)

    # Process the messages
    # pprint.pprint(messages)
    # messages_to_html(messages)
    # visualize_messages_markdown(messages)
    visualize_messages_jupyter(messages)
    # key_list = [print(list((key,message[key]) if key!='content' else (key,list(map(lambda x: x["type"],  message[key]))) for key in message.keys())) for message in messages]


if __name__ == "__main__":
    main()
