from bottle import Bottle, run
from bottle_autodocs import bottle_autodocs

app = Bottle()

auto_docs = bottle_autodocs.BottleAutoDocs(title="My API", version="1.0.0", description="My API Docs",terms_of_service="http://example.com/terms/",
    contact={
        "name": "name of author",
        "url": "http://url.example.com/contact/",
        "email": "author.example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://license_link.com",
    },summary="This is the main summary ")
app.install(auto_docs)





if __name__ == '__main__':
    run(app, host='localhost', port=8080, debug=True)
