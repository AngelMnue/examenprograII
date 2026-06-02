import os
import sqlite3
from flask import Flask, request, jsonify
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


# --- RUTAS / ENDPOINTS (API REST) ---

@app.route('/api/login', methods=['POST'])
def api_login():
    """API JSON: Verifica credenciales de usuario"""
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM usuarios WHERE username = ? AND password = ?',
                        (username, password)).fetchone()
    conn.close()
    
    if user:
        return jsonify({'success': True, 'nombre': user['nombre']})
    else:
        return jsonify({'success': False, 'msg': "Credenciales incorrectas."}), 401

@app.route('/api/buscar_producto', methods=['POST'])
def buscar_producto():
    """API JSON: retorna datos del producto buscado."""
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)