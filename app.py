import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'clave_secreta_para_desarrollo_unfv')
CORS(app)  

DATABASE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa la base de datos con tablas y datos de prueba si no existen."""
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
    
        conn.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                nombre TEXT NOT NULL
            )
        ''')
       
        conn.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                precio REAL NOT NULL,
                stock INTEGER NOT NULL,
                categoria TEXT
            )
        ''')
        
     
        conn.execute("INSERT INTO usuarios (username, password, nombre) VALUES (?, ?, ?)",
                     ('admin', 'admin123', 'Angel Manuel Quispe Congona'))
        
        productos_semilla = [
            ('P001', 'Laptop Ryzen 5', '8GB RAM, 512GB SSD M.2 NVMe', 2500.00, 15, 'Cómputo'),
            ('P002', 'Procesador Ryzen 5 7600X', '6 núcleos, 4.7GHz hasta 5.3GHz', 1150.00, 8, 'Componentes'),
            ('P003', 'SSD 1TB Kingston', 'NVMe PCIe 4.0 M.2', 320.00, 25, 'Almacenamiento'),
            ('P004', 'Procesador Ryzen 5 8500G', 'Con gráficos integrados Radeon 740M', 890.00, 12, 'Componentes')
        ]
        conn.executemany("INSERT INTO productos (codigo, nombre, descripcion, precio, stock, categoria) VALUES (?, ?, ?, ?, ?, ?)", 
                         productos_semilla)
        
        conn.commit()
        conn.close()


init_db()


@app.route('/')
def index():
    """Redirige automáticamente al login[cite: 18]."""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Muestra y procesa el formulario de acceso[cite: 18]."""
    msg = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM usuarios WHERE username = ? AND password = ?',
                            (username, password)).fetchone()
        conn.close()
        
        if user:
            session['logged_in'] = True
            session['username'] = user['username']
            session['nombre'] = user['nombre']
            return redirect(url_for('principal'))
        else:
            msg = "Credenciales incorrectas. Inténtelo de nuevo."
            
    return render_template('login.html', msg=msg)

@app.route('/principal')
def principal():
    """Panel principal (requiere sesión activa)[cite: 18]."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('principal.html', nombre=session.get('nombre'))

@app.route('/buscador')
def buscador():
    """Formulario de búsqueda de productos[cite: 18]."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('buscador.html')

@app.route('/api/buscar_producto', methods=['POST'])
def buscar_producto():
    """API JSON: retorna datos del producto buscado[cite: 18]."""
    if not session.get('logged_in'):
        return jsonify({'error': 'No autorizado'}), 401
        
    data = request.get_json()
    codigo = data.get('codigo', '').strip()
    
    conn = get_db_connection()
    producto = conn.execute('SELECT * FROM productos WHERE codigo = ?', (codigo,)).fetchone()
    conn.close()
    
    if producto:
        return jsonify({
            'encontrado': True,
            'codigo': producto['codigo'],
            'nombre': producto['nombre'],
            'descripcion': producto['descripcion'],
            'precio': producto['precio'],
            'stock': producto['stock'],
            'categoria': producto['categoria']
        })
    else:
        return jsonify({'encontrado': False, 'msg': 'Producto no encontrado'})

@app.route('/logout')
def logout():
    """Cierra sesión y redirige al login[cite: 18]."""
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)