"""
Script para crear datos de prueba en el sistema.
"""
from app import crear_app
from app.core.extensions import db
from app.models import Usuario, Producto, Categoria, Proveedor
from werkzeug.security import generate_password_hash

app = crear_app()

with app.app_context():
    print("🔧 Creando datos de prueba...")
    
    # Crear usuario administrador
    admin = Usuario.query.filter_by(email='admin@inventario.com').first()
    if not admin:
        admin = Usuario(
            email='admin@inventario.com',
            nombre_completo='Administrador del Sistema',
            rol='DUENO',
            esta_activo=True
        )
        admin.establecer_password('admin123')
        db.session.add(admin)
        print("✅ Usuario admin creado: admin@inventario.com / admin123")
    else:
        print("ℹ️  Usuario admin ya existe")
    
    # Crear categorías
    categorias_data = [
        {'nombre': 'Electrónica', 'descripcion': 'Productos electrónicos'},
        {'nombre': 'Alimentos', 'descripcion': 'Productos alimenticios'},
        {'nombre': 'Bebidas', 'descripcion': 'Bebidas y refrescos'},
        {'nombre': 'Limpieza', 'descripcion': 'Productos de limpieza'},
    ]
    
    categorias = {}
    for cat_data in categorias_data:
        cat = Categoria.query.filter_by(nombre=cat_data['nombre']).first()
        if not cat:
            cat = Categoria(**cat_data)
            db.session.add(cat)
        categorias[cat_data['nombre']] = cat
    
    db.session.commit()
    print(f"✅ {len(categorias_data)} categorías creadas")
    
    # Crear proveedores
    proveedores_data = [
        {
            'nombre': 'Distribuidora Central',
            'ruc': '123-4567890-1',
            'telefono': '(809) 555-1234',
            'email': 'ventas@distribuidoracentral.com',
            'direccion': 'Av. Principal #123, Santo Domingo'
        },
        {
            'nombre': 'Importadora Global',
            'ruc': '987-6543210-2',
            'telefono': '(809) 555-5678',
            'email': 'contacto@importadoraglobal.com',
            'direccion': 'Calle Comercio #456, Santiago'
        },
    ]
    
    proveedores = {}
    for prov_data in proveedores_data:
        prov = Proveedor.query.filter_by(nombre=prov_data['nombre']).first()
        if not prov:
            prov = Proveedor(**prov_data)
            db.session.add(prov)
        proveedores[prov_data['nombre']] = prov
    
    db.session.commit()
    print(f"✅ {len(proveedores_data)} proveedores creados")
    
    # Crear productos de ejemplo
    productos_data = [
        {
            'codigo_sku': 'ELEC-001',
            'nombre': 'Laptop HP 15"',
            'descripcion': 'Laptop HP 15 pulgadas, 8GB RAM, 256GB SSD',
            'categoria': categorias['Electrónica'],
            'stock_minimo': 5,
            'stock_maximo': 20,
            'cantidad_actual': 3,  # Bajo stock para probar alertas
            'unidad_medida': 'UNIDAD',
            'precio_venta': 25000.00,
            'costo_promedio': 18000.00,
            'margen_deseado': 35.0,
        },
        {
            'codigo_sku': 'ALIM-001',
            'nombre': 'Arroz Blanco 5lb',
            'descripcion': 'Arroz blanco premium, bolsa de 5 libras',
            'categoria': categorias['Alimentos'],
            'stock_minimo': 50,
            'stock_maximo': 200,
            'cantidad_actual': 120,
            'unidad_medida': 'UNIDAD',
            'precio_venta': 250.00,
            'costo_promedio': 180.00,
            'margen_deseado': 30.0,
        },
        {
            'codigo_sku': 'BEB-001',
            'nombre': 'Coca Cola 2L',
            'descripcion': 'Refresco Coca Cola 2 litros',
            'categoria': categorias['Bebidas'],
            'stock_minimo': 30,
            'stock_maximo': 100,
            'cantidad_actual': 25,  # Bajo stock
            'unidad_medida': 'UNIDAD',
            'precio_venta': 120.00,
            'costo_promedio': 85.00,
            'margen_deseado': 35.0,
        },
        {
            'codigo_sku': 'LIMP-001',
            'nombre': 'Detergente Tide 1kg',
            'descripcion': 'Detergente en polvo Tide 1 kilogramo',
            'categoria': categorias['Limpieza'],
            'stock_minimo': 20,
            'stock_maximo': 80,
            'cantidad_actual': 45,
            'unidad_medida': 'UNIDAD',
            'precio_venta': 350.00,
            'costo_promedio': 250.00,
            'margen_deseado': 35.0,
        },
    ]
    
    for prod_data in productos_data:
        prod = Producto.query.filter_by(codigo_sku=prod_data['codigo_sku']).first()
        if not prod:
            prod = Producto(**prod_data)
            db.session.add(prod)
    
    db.session.commit()
    print(f"✅ {len(productos_data)} productos de ejemplo creados")
    
    print("\n🎉 ¡Datos de prueba creados exitosamente!")
    print("\n📝 Credenciales de acceso:")
    print("   Email: admin@inventario.com")
    print("   Password: admin123")
    print("\n🌐 Accede al sistema en: http://localhost:3000")
