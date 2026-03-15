from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
import phonenumbers

app = Flask(__name__)
app.secret_key = 'secret_key'

def get_db():
    return psycopg2.connect(
        host="postgres",
        database="phonebook",
        user="admin",
        password="admin"
    )

def check_number(phone):
    try:
        parsed_number = phonenumbers.parse(phone, "RU")
        is_valid = phonenumbers.is_valid_number(parsed_number)
        is_possible = phonenumbers.is_possible_number(parsed_number)
        if not is_valid or not is_possible:
            flash('Invalid phone number', 'error')
            return False
        return True
    except phonenumbers.NumberParseException as e:
        flash(f'invalid phone number', 'error')
    except Exception as e:
        flash(f'unexpected problems: {e}', 'error')
        return False

@app.route('/')
def index():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, surname, phone, note FROM contacts ORDER BY id")
    contacts = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', contacts=contacts)

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    surname = request.form['surname']
    phone = request.form['phone']
    note = request.form['note']
    conn = get_db()
    cur = conn.cursor()
    if not check_number(phone):
        return redirect(url_for('index'))
    cur.execute("INSERT INTO contacts (name, surname, phone, note) VALUES (%s, %s, %s, %s)", (name, surname, phone, note))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))


@app.route('/edit/<int:id>')
def edit(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, surname, phone, note FROM contacts WHERE id = %s", (id,))
    contact = cur.fetchone()
    cur.close()
    conn.close()
    
    if contact is None:
        flash("Number not found!", 'error')
        return redirect(url_for('edit'))
        
    return render_template('edit.html', contact=contact)

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    id = request.form['id']
    name = request.form['name']
    surname = request.form['surname']
    phone = request.form['phone']
    note = request.form['note']
    conn = get_db()
    cur = conn.cursor()
    if name:
        cur.execute("UPDATE contacts SET name = %s WHERE id = %s", (name, id))
    if surname:
        cur.execute("UPDATE contacts SET surname = %s WHERE id = %s", (surname, id))
    if phone:
        if not check_number(phone):
            return redirect(url_for('edit', id=id))
        cur.execute("UPDATE contacts SET phone = %s WHERE id = %s", (phone, id))
    if note:
        cur.execute("UPDATE contacts SET note = %s WHERE id = %s", (note, id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM contacts WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)