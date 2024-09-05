import os  # Add this import statement
from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for, flash
from pymongo import MongoClient
from datetime import datetime, timedelta
import csv
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a real secret key in production

# Initialize MongoDB client
mongodb_uri = os.getenv('MONGODB_URI')
client = MongoClient(mongodb_uri)

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"An error occurred: {e}")

db = client['journaling']  # Create or connect to a MongoDB database named 'journaling'
entries_collection = db['entries']  # Create or connect to a collection named 'entries'

# Route to display the journal entry form
@app.route('/')
def index():
    return render_template('index.html', entry=None, timedelta=timedelta)  # Pass timedelta to the template

# Route to handle form submission and insert or update journal entry into MongoDB
@app.route('/add_entry', methods=['POST'])
def add_entry():
    try:
        # Collect form data
        entry_data = {
            'date': datetime.strptime(request.form['date'], '%Y-%m-%d') if request.form['date'] else None,
            'weight': float(request.form['weight']) if request.form['weight'] else None,
            'calories': int(request.form['calories']) if request.form['calories'] else None,
            'steps': int(request.form['steps']) if request.form['steps'] else None,
            'time_up': request.form['time_up'],
            'time_bed': request.form['time_bed'],
            'time_first_food': request.form['time_first_food'],
            'diary': request.form['diary'],
            'orla': request.form['orla'],
            'conor': request.form['conor'],
            'anne': request.form['anne'],
            'health_problems': request.form['health_problems'],
            'weather': request.form['weather'],
            'exercise': request.form['exercise'],
            'dinner': request.form['dinner'],
            'tv': request.form['tv'],
            'beer': int(request.form['beer']) if request.form['beer'] else None,
            'wine': int(request.form['wine']) if request.form['wine'] else None,
            'spirit': int(request.form['spirit']) if request.form['spirit'] else None,
            'gars': int(request.form['gars']) if request.form['gars'] else None
        }

        # Check if an entry exists for the given date
        existing_entry = entries_collection.find_one({'date': entry_data['date']})

        if existing_entry:
            # Update existing entry
            entries_collection.update_one({'_id': existing_entry['_id']}, {'$set': entry_data})
            flash('Entry updated successfully!', 'success')
        else:
            # Insert new entry
            entries_collection.insert_one(entry_data)
            flash('Entry added successfully!', 'success')

        return redirect(url_for('index'))
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('index'))

# Route to handle loading an entry based on the selected date
@app.route('/load_entry', methods=['GET'])
def load_entry():
    try:
        selected_date = request.args.get('date')
        print(f"Received date from request: {selected_date}")  # Debugging statement

        if selected_date:
            # Convert selected_date to a datetime object using the correct format
            entry_date = datetime.strptime(selected_date, '%Y-%m-%d')
            print(f"Parsed date object: {entry_date}")  # Debugging statement

            # Find the entry with the given date
            entry = entries_collection.find_one({'date': entry_date})

            if entry:
                # Convert the entry's ObjectId to a string for the template
                entry['_id'] = str(entry['_id'])
                print(f"Found entry: {entry}")  # Debugging statement
                return render_template('index.html', entry=entry, timedelta=timedelta)  # Pass timedelta

        flash('No entry found for the selected date.', 'info')
        return redirect(url_for('index'))
    except Exception as e:
        print(f"An error occurred: {e}")  # Debugging statement
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('index'))




# Route to display stored journal entries
@app.route('/view_entries')
def view_entries():
    try:
        # Fetch all entries from MongoDB and sort by date (newest first)
        entries = list(entries_collection.find().sort('date', -1))

        # Convert the date field to a more readable format
        #for entry in entries:
        #    entry['date'] = entry['date'].strftime('%Y-%m-%d') if entry['date'] else 'N/A'

        return render_template('view_entries.html', entries=entries)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# Route to handle updating an entry
@app.route('/update_entry/<entry_id>', methods=['POST'])
def update_entry(entry_id):
    try:
        # Collect updated data from the form
        updated_data = {
            'date': datetime.strptime(request.form['date'], '%Y-%m-%d') if request.form['date'] else None,
            'weight': float(request.form['weight']) if request.form['weight'] else None,
            'calories': int(request.form['calories']) if request.form['calories'] else None,
            'steps': int(request.form['steps']) if request.form['steps'] else None,
            'time_up': request.form['time_up'],
            'time_bed': request.form['time_bed'],
            'time_first_food': request.form['time_first_food'],
            'diary': request.form['diary'],
            'orla': request.form['orla'],
            'conor': request.form['conor'],
            'anne': request.form['anne'],
            'health_problems': request.form['health_problems'],
            'weather': request.form['weather'],
            'exercise': request.form['exercise'],
            'dinner': request.form['dinner'],
            'tv': request.form['tv'],
            'beer': int(request.form['beer']) if request.form['beer'] else None,
            'wine': int(request.form['wine']) if request.form['wine'] else None,
            'spirit': int(request.form['spirit']) if request.form['spirit'] else None,
            'gars': int(request.form['gars']) if request.form['gars'] else None
        }

        # Update the entry in the MongoDB collection
        entries_collection.update_one({'_id': entry_id}, {'$set': updated_data})

        flash('Entry updated successfully!', 'success')
        return redirect(url_for('view_entries'))
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('view_entries'))


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
        writer.writerow([
            'Date', 'Weight', 'MyFitnessPal Calories Remaining', 'Step Count', 
            'Time Up', 'Time In Bed', 'Time of First Food', 'Diary', 'Orla', 
            'Conor', 'Anne', 'Health Problems', 'Weather', 'Exercise', 'Dinner', 
            'Watched on TV', 'Beer x330ml', 'Wine x175ml', 'Spirit x35ml', 'Gars'
        ])

        # Write each entry to the CSV file
        for entry in entries:
            writer.writerow([
                entry.get('date').strftime('%Y-%m-%d') if entry.get('date') else '',
                entry.get('weight', ''),
                entry.get('calories', ''),
                entry.get('steps', ''),
                entry.get('time_up', ''),
                entry.get('time_bed', ''),
                entry.get('time_first_food', ''),
                entry.get('diary', ''),
                entry.get('orla', ''),
                entry.get('conor', ''),
                entry.get('anne', ''),
                entry.get('health_problems', ''),
                entry.get('weather', ''),
                entry.get('exercise', ''),
                entry.get('dinner', ''),
                entry.get('tv', ''),
                entry.get('beer', ''),
                entry.get('wine', ''),
                entry.get('spirit', ''),
                entry.get('gars', '')
            ])

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
    app.run(debug=True)
