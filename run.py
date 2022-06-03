from app import init_app

# Entry Point fo the App
app = init_app()
if __name__ == "__main__":
    app.run(debug=True)