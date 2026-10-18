from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from stego_engine import (
    encode_image, decode_image, 
    encode_image_in_image, decode_image_from_image,
    encode_dual_stego, decode_dual_stego
)
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

LIBRARY_DATA = {
    "Academic & Textbooks": [
        {"title": "Concise Physics Class XII", "info": "Available — Section A, Shelf 1 (Acc No: 1001)"},
        {"title": "Chemistry Part 1 Class 12", "info": "Available — Section A, Shelf 2 (Acc No: 1002)"},
        {"title": "Computer Science with Python Sumita Arora", "info": "Available — CS Section, Shelf 1 (Acc No: 1003)"},
        {"title": "Mathematics Volume 1 RD Sharma", "info": "Issued — Expected return in 2 days (Acc No: 1004)"},
        {"title": "Biology Class 12 NCERT", "info": "Available — Section A, Shelf 4 (Acc No: 1005)"},
        {"title": "Macroeconomics Class 12", "info": "Available — Section B, Shelf 1 (Acc No: 1006)"},
        {"title": "Accountancy Part I", "info": "Available — Section B, Shelf 2 (Acc No: 1007)"},
        {"title": "Business Studies Class 12", "info": "Available — Section B, Shelf 3 (Acc No: 1008)"},
        {"title": "Indian Economic Development", "info": "Available — Section B, Shelf 4 (Acc No: 1009)"},
        {"title": "English Core Flamingo", "info": "Available — Section C, Shelf 1 (Acc No: 1010)"}
    ],
    "Computer Science & Tech": [
        {"title": "Python Crash Course", "info": "Available — CS Section, Shelf 2 (Acc No: 2001)"},
        {"title": "Clean Code Robert Martin", "info": "Available — CS Section, Shelf 3 (Acc No: 2002)"},
        {"title": "Introduction to Algorithms Cormen", "info": "Reference Only — Main Reading Room (Acc No: 2003)"},
        {"title": "Automating the Boring Stuff with Python", "info": "Available — CS Section, Shelf 2 (Acc No: 2004)"},
        {"title": "Design Patterns Gang of Four", "info": "Available — CS Section, Shelf 4 (Acc No: 2005)"},
        {"title": "The Pragmatic Programmer", "info": "Issued — Expected return tomorrow (Acc No: 2006)"},
        {"title": "Head First Java", "info": "Available — CS Section, Shelf 3 (Acc No: 2007)"},
        {"title": "Data Structures and Algorithms in Python", "info": "Available — CS Section, Shelf 1 (Acc No: 2008)"}
    ],
    "Popular Science": [
        {"title": "Brief Answers to the Big Questions Stephen Hawking", "info": "Available — Science Wing, Shelf 1 (Acc No: 3001)"},
        {"title": "Sapiens Yuval Noah Harari", "info": "Available — General Non-Fiction, Shelf 3 (Acc No: 3002)"},
        {"title": "Cosmos Carl Sagan", "info": "Available — Science Wing, Shelf 2 (Acc No: 3003)"},
        {"title": "The Selfish Gene Richard Dawkins", "info": "Available — Science Wing, Shelf 3 (Acc No: 3004)"},
        {"title": "What If Randall Munroe", "info": "Available — Science Wing, Shelf 4 (Acc No: 3005)"},
        {"title": "Thinking Fast and Slow", "info": "Available — Psychology Section, Shelf 1 (Acc No: 3006)"}
    ],
    "Self-Improvement": [
        {"title": "Atomic Habits James Clear", "info": "Issued — Expected return in 5 days (Acc No: 4001)"},
        {"title": "Deep Work Cal Newport", "info": "Available — Self-Help Section, Shelf 1 (Acc No: 4002)"},
        {"title": "The Psychology of Money Morgan Housel", "info": "Available — Self-Help Section, Shelf 2 (Acc No: 4003)"},
        {"title": "Ikigai", "info": "Available — Self-Help Section, Shelf 2 (Acc No: 4004)"},
        {"title": "Rich Dad Poor Dad", "info": "Issued — Reserved by Library Staff (Acc No: 4005)"},
        {"title": "Can't Hurt Me David Goggins", "info": "Available — Self-Help Section, Shelf 3 (Acc No: 4006)"},
        {"title": "Make Your Bed", "info": "Available — Self-Help Section, Shelf 4 (Acc No: 4007)"}
    ],
    "Classic & Indian Literature": [
        {"title": "To Kill a Mockingbird Harper Lee", "info": "Available — Literature, Shelf 1 (Acc No: 5001)"},
        {"title": "1984 George Orwell", "info": "Available — Literature, Shelf 2 (Acc No: 5002)"},
        {"title": "Pride and Prejudice Jane Austen", "info": "Available — Literature, Shelf 3 (Acc No: 5003)"},
        {"title": "Malgudi Days R K Narayan", "info": "Available — Indian Auth, Shelf 1 (Acc No: 6001)"},
        {"title": "The God of Small Things Arundhati Roy", "info": "Available — Indian Auth, Shelf 2 (Acc No: 6002)"},
        {"title": "Wings of Fire A P J Abdul Kalam", "info": "Available — Biography Wing, Shelf 1 (Acc No: 6004)"},
        {"title": "Ignited Minds A P J Abdul Kalam", "info": "Available — Biography Wing, Shelf 1 (Acc No: 6006)"}
    ],
    "Fiction, Mystery & Sci-Fi": [
        {"title": "Dune Frank Herbert", "info": "Available — Fiction, Shelf 4 (Acc No: 7001)"},
        {"title": "The Hobbit J R R Tolkien", "info": "Available — Fiction, Shelf 5 (Acc No: 7002)"},
        {"title": "Sherlock Holmes Arthur Conan Doyle", "info": "Available — Mystery, Shelf 1 (Acc No: 7003)"},
        {"title": "And Then There Were None Agatha Christie", "info": "Available — Mystery, Shelf 2 (Acc No: 7004)"},
        {"title": "The Da Vinci Code Dan Brown", "info": "Available — Thriller, Shelf 1 (Acc No: 7005)"},
        {"title": "Harry Potter and the Sorcerer's Stone", "info": "Issued — Expected return tomorrow (Acc No: 7006)"}
    ]
}

@app.route('/')
def home():
    genres = list(LIBRARY_DATA.keys())
    return render_template('library.html', genres=genres)

@app.route('/get_books_by_genre', methods=['POST'])
def get_books_by_genre():
    selected_genre = request.json.get('genre')
    books = LIBRARY_DATA.get(selected_genre, [])
    titles = [b['title'] for b in books]
    return jsonify({'books': titles})

@app.route('/search_book', methods=['POST'])
def search_book():
    title = request.form.get('book_title', '').strip().lower()
    serial = request.form.get('book_no', '').strip()

    if title == 'mythios' and serial == '3695':
        return jsonify({'status': 'covert_unlock', 'redirect': '/vault'})

    for genre, book_list in LIBRARY_DATA.items():
        for b in book_list:
            if title in b['title'].lower() or b['title'].lower() in title:
                return jsonify({'status': 'normal', 'message': f"STATUS: {b['info']}"})

    return jsonify({'status': 'normal', 'message': f'Book "{title.title()}" (Serial: {serial}) is currently not available in catalog.'})

@app.route('/vault')
def vault():
    return render_template('vault.html')

# ROUTE TO SERVE UPLOADED/EXTRACTED FILES DIRECTLY
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/encode', methods=['POST'])
def encode():
    if 'image' not in request.files: return "No image uploaded", 400
    file = request.files['image']
    message = request.form.get('message', '')
    key = request.form.get('key', '')
    
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    output_filename = "stego_" + os.path.splitext(file.filename)[0] + ".png"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    file.save(input_path)
    encode_image(input_path, message, key, output_path)
    return send_file(output_path, as_attachment=True, download_name=output_filename, mimetype='image/png')

@app.route('/decode', methods=['POST'])
def decode():
    if 'stego_image' not in request.files: return jsonify({'success': False, 'result': 'No image uploaded'})
    file = request.files['stego_image']
    key = request.form.get('key', '')
    
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], "temp_" + file.filename)
    file.save(input_path)
    success, result = decode_image(input_path, key)
    if os.path.exists(input_path): os.remove(input_path)
    return jsonify({'success': success, 'result': result})

@app.route('/encode_img', methods=['POST'])
def encode_img():
    if 'cover_image' not in request.files or 'secret_image' not in request.files: return "Missing images", 400
    cover = request.files['cover_image']
    secret = request.files['secret_image']
    
    cover_path = os.path.join(app.config['UPLOAD_FOLDER'], "cover_" + cover.filename)
    secret_path = os.path.join(app.config['UPLOAD_FOLDER'], "secret_" + secret.filename)
    output_filename = "stego_img_" + os.path.splitext(cover.filename)[0] + ".png"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    cover.save(cover_path)
    secret.save(secret_path)
    encode_image_in_image(cover_path, secret_path, output_path)
    
    if os.path.exists(cover_path): os.remove(cover_path)
    if os.path.exists(secret_path): os.remove(secret_path)
    return send_file(output_path, as_attachment=True, download_name=output_filename, mimetype='image/png')

@app.route('/decode_img', methods=['POST'])
def decode_img():
    if 'stego_image' not in request.files: return "No image uploaded", 400
    file = request.files['stego_image']
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], "temp_" + file.filename)
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], "extracted_secret.png")
    
    file.save(input_path)
    decode_image_from_image(input_path, output_path)
    if os.path.exists(input_path): os.remove(input_path)
    return send_file(output_path, as_attachment=True, download_name="extracted_secret.png", mimetype='image/png')

@app.route('/encode_dual', methods=['POST'])
def encode_dual():
    if 'cover_image' not in request.files or 'secret_image' not in request.files: return "Missing files", 400
    cover = request.files['cover_image']
    secret_img = request.files['secret_image']
    message = request.form.get('message', '')
    
    cover_path = os.path.join(app.config['UPLOAD_FOLDER'], "dual_cover_" + cover.filename)
    secret_path = os.path.join(app.config['UPLOAD_FOLDER'], "dual_secret_" + secret_img.filename)
    output_filename = "dual_stego_" + os.path.splitext(cover.filename)[0] + ".png"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    cover.save(cover_path)
    secret_img.save(secret_path)
    encode_dual_stego(cover_path, secret_path, message, output_path)
    
    if os.path.exists(cover_path): os.remove(cover_path)
    if os.path.exists(secret_path): os.remove(secret_path)
    return send_file(output_path, as_attachment=True, download_name=output_filename, mimetype='image/png')

@app.route('/decode_dual', methods=['POST'])
def decode_dual():
    if 'stego_image' not in request.files: return jsonify({'success': False, 'result': 'No image uploaded'})
    file = request.files['stego_image']
    
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], "temp_dual_" + file.filename)
    extracted_img_path = os.path.join(app.config['UPLOAD_FOLDER'], "extracted_dual_secret.png")
    file.save(input_path)
    
    success, result_text = decode_dual_stego(input_path, extracted_img_path)
    if os.path.exists(input_path): os.remove(input_path)
    
    return jsonify({
        'success': success,
        'result_text': result_text,
        'extracted_image_url': '/uploads/extracted_dual_secret.png'
    })

if __name__ == '__main__':
    app.run(debug=True)