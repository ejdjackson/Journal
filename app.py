from flask import Flask, request, jsonify, render_template, send_file
from pymongo import MongoClient
from datetime import datetime
import csv
import io

# Initialize Flask app
app = Flask(__name__)

# Initialize MongoDB client
client = MongoClient("mongodb://localhost:27017/")
db = client['journaling']  # Create or connect to a MongoDB database named 'journaling'
entries_collection = db['entries']  # Create or connect to a collection named 'entries'

# Route to display the journal entry form
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle form submission and insert journal entry into MongoDB
@app.route('/add_entry', methods=['POST'])
def add_entry():
    try:
        # Get data from the form
        entry_date = request.form.get('date')
        entry_text = request.form.get('entry')

        # Convert the date from string to datetime object
        entry_date = datetime.strptime(entry_date, '%Y-%m-%d')

        # Create an entry object
        entry = {
            'date': entry_date,
            'entry': entry_text
        }

        # Insert entry into MongoDB
        entries_collection.insert_one(entry)

        return jsonify({'status': 'success', 'message': 'Entry added successfully!'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# Route to display stored journal entries
@app.route('/view_entries')
def view_entries():
    try:
        # Fetch all entries from MongoDB and sort by date (newest first)
        entries = list(entries_collection.find().sort('date', -1))

        # Convert the date field to a more readable format
        for entry in entries:
            entry['date'] = entry['date'].strftime('%Y-%m-%d')

        return render_template('view_entries.html', entries=entries)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# Route to export entries as a CSV file
@app.route('/export_csv')
def export_csv():
    try:
        # Fetch all entries from MongoDB
        entries = list(entries_collection.find())

        # Create an in-memory text stream
        output = io.StringIO()
        writer = csv.writer(output)

        # Write the header row to the CSV file
        writer.writerow(['Date', 'Entry'])

        # Write each entry to the CSV file
        for entry in entries:
            writer.writerow([entry['date'].strftime('%Y-%m-%d'), entry['entry']])

        # Get the string from the StringIO object and encode it to bytes
        output.seek(0)
        csv_data = output.getvalue().encode('utf-8')

        # Create a BytesIO object from the encoded CSV data
        output_bytes = io.BytesIO(csv_data)

        # Return the CSV file as a downloadable file
        return send_file(output_bytes, mimetype='text/csv', as_attachment=True, download_name='journal_entries.csv')

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True)
