from flask import Flask, request, redirect, render_template,send_file
from io import BytesIO
from redis_client import Redis
import base64 
from file_python import File 


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Add a secret key for session management
# Connect to Redis (replace with your connection details)
 
server_address="localhost"
redis_port="6379"
redis_pass="password123"
redis_cli = Redis(server_address, redis_port, redis_pass)

file=File()

@app.route('/save-text', methods=['POST'])
def save_text():
    text = request.form['text']
    if not text:
        return "Text input required! Please provide text in the form."
    save_as_file = 'save_as_file' in request.form
    if save_as_file:
        # filename=f'{uuid.uuid1()}'+".txt"
        filename="save-text.txt"
        send_to = request.form['send_to_save']
        if not send_to:
            return "send_to required! Please provide send_to in the form."
        encoded_data = base64.b64encode(text.encode('utf-8')).decode('utf-8')
         # Convert file to bytes 
        data_length = len(encoded_data)

        # Get send_to from form or session (assuming send_to input is required)
        
        key = f"file_{send_to}_{filename}"
            # Check if file exists in Redis
        if redis_cli.key_exists(key):
            return render_template('file_exists.html', send_to=send_to, filename=filename, encoded_data=encoded_data)
        for i in range(0, data_length, 1048576):
                redis_cli.appendRpush(key, encoded_data[i:i+1048576])
        message=f"File '{filename}' uploaded successfully!" 
        options = update_file_list('farman', 'admin')
        return render_template('index.html', options=options, message=message,retrieved_text=getText())
    redis_cli.setKey('saved_text', text)
    options = update_file_list('farman', 'admin')
    return render_template('index.html', options=options, message="Text saved successfully!",retrieved_text=getText())

def getText():
    text = redis_cli.getKey('saved_text')
    if not text:
        text = "No text found in Redis."
    return text

@app.route('/download-text', methods=['POST'])
def download_retrieved_text():
    retrieved_text = request.form['retrieved_text']
    return send_file(BytesIO(retrieved_text.encode()), as_attachment=True, download_name='retrieved_text.txt', mimetype='text/plain')


@app.route('/get-text', methods=['GET'])
def get_text():
    options = update_file_list('farman', 'admin')
    return render_template('index.html', options=options, message=None,retrieved_text=getText())

def update_file_list(send_to,role):
    if not redis_cli.isConnected():
        redis_cli.connect()
        if not redis_cli.isConnected():
             return None
    if role=="admin":
        pattern = "file_"+"*"+"_*"
    else:
        pattern = "file_*"+""+send_to+""+"_*"
 
    result = redis_cli.getAllKeys(pattern)
    options={}
    for file_key in result:

        # new_list = file_key.split("_")
        # file_name = "_".join(new_list[2:])
        options[file_key]=file_key
    return options

 
@app.route('/download', methods=['POST'])
def download():
    selected_option = request.form['selected_option']
    # Get corresponding value

    # Perform an action based on the selected option (replace with your logic)
    encoded_data_list = redis_cli.getKey(selected_option)
    if encoded_data_list is None:
        return 'Invalid Data'
  # Assuming the data is stored as a list of base64 strings in Redis
    encoded_data = ""
    for data in encoded_data_list:
        encoded_data += data
    decoded_data = base64.b64decode(encoded_data.encode())
    filename="_".join(selected_option.split("_")[2:])
    # Use a BytesIO stream to send the decoded data as a file
    return send_file(BytesIO(decoded_data), as_attachment=True, download_name=filename)

@app.route('/overwrite', methods=['POST'])
def overwrite():
    send_to = request.form['send_to']
    filename = request.form['filename']
    encoded_data = request.form['encoded_data']
    key = f"file_{send_to}_{filename}"

    # Remove existing file data
    redis_cli.deleteKey(key)

    # Save data to Redis in chunks
    data_length = len(encoded_data)
    for i in range(0, data_length, 1048576):
        redis_cli.appendRpush(key, encoded_data[i:i+1048576])

    options = update_file_list('farman', 'admin')
    return render_template('index.html', options=options, message=f"File '{filename}' overwritten successfully!",retrieved_text=getText())


@app.route('/rename', methods=['POST'])
def rename():
    send_to = request.form['send_to']
    encoded_data = request.form['encoded_data']
    new_filename = request.form['new_filename']
    if not new_filename:
        return "New filename required! Please provide a new filename."
    
    key = f"file_{send_to}_{new_filename}"

    if redis_cli.key_exists(key):
        return render_template('file_exists.html', send_to=send_to, filename=new_filename, encoded_data=encoded_data)

    # Save data to Redis in chunks
    data_length = len(encoded_data)
    for i in range(0, data_length, 1048576):
        redis_cli.appendRpush(key, encoded_data[i:i+1048576])

    return render_template('index.html', options=update_file_list('farman','admin'), message=f"File '{new_filename}' renamed and uploaded successfully!",retrieved_text=getText())
 

 
@app.route('/', methods=['GET', 'POST'])
def index():
    options=update_file_list('farman','admin')
    if request.method == 'POST':
            send_to = request.form['send_to']
            if not send_to:
                return "send_to required! Please provide send_to in the form."
            encoded_data=None
            filename=None
            # Check if file is uploaded
            # Check if the post request has the file part
            if 'folder' in request.files:
                files = request.files.getlist('folder')
                encoded_data = file.zip_in_memory_fileStorage(files)
                filename=request.form['filename']
                if filename:
                    filename=filename+".zip"
            elif 'file' in request.files:
                files = request.files['file']
                filename = files.filename
                encoded_data=base64.b64encode(files.read()).decode('utf-8')
            if encoded_data is None:
                return 'No file Selection'
            if filename is None:
                return 'No file Selected'

            # Convert file to bytes
            data_length = len(encoded_data)

            # Get send_to from form or session (assuming send_to input is required)
            
            key = f"file_{send_to}_{filename}"
                # Check if file exists in Redis
            if redis_cli.key_exists(key):
                return render_template('file_exists.html', send_to=send_to, filename=filename, encoded_data=encoded_data)
            # Efficiently save data to Redis in chunks
            for i in range(0, data_length, 1048576):
                redis_cli.appendRpush(key, encoded_data[i:i+1048576])
 
            return f"File '{filename}' uploaded successfully!"

    # Render the template with options for the dropdown initially
    return render_template('index.html', options=options, message=None,retrieved_text=getText())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')