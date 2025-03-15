from bottle import Bottle, run , request
from bottle_autodocs import bottle_autodocs

app = Bottle()


UPLOAD_PATH = r'\downloads' # Make sure this folder exist or change name to a folder that exists

# Install the plugin
auto_docs = bottle_autodocs.BottleAutoDocs(title="My API", version="1.0.0", description="API Docs File Uploads ")
app.install(auto_docs)


@app.route('/multiupload', method='POST', summary="This is summary for multi file upload", description="This is desc for multi file upload")
def upload_files():
    # Get the list of files
    uploads = request.files.getall('files')  # Use getall() to handle multiple files
    metadata = request.forms.get('metadata')
    meta = request.forms.get('meta')

    if not uploads:
        return {"error": "No files provided"}

    saved_files = []
    for upload in uploads:
        file_path = f"{UPLOAD_PATH}/{upload.filename}"
        upload.save(file_path)  # Save file to UPLOAD_PATH
        saved_files.append(upload.filename)

    return {
        "message": f"{len(saved_files)} files uploaded successfully",
        "uploaded_files": saved_files,
        "metadata": metadata,
        'meta': meta
    }


@app.route('/upload', method='POST', summary="This is summary for single file upload", description="This is desc for single file upload")
def upload_file():
    # Get the list of files
    upload = request.files.get('file')  # Use getall() to handle multiple files
    metadata = request.forms.get('metadata')

    if not upload:
        return {"error": "No files provided"}

    file_path = f"{UPLOAD_PATH}/{upload.filename}"
    upload.save(file_path) 


    return {
        "message": f" files uploaded successfully",
        "metadata": metadata,
    }


if __name__ == '__main__':
    run(app, host='localhost', port=8080, debug=True)
