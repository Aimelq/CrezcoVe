"""
Script para crear usuario administrador inicial.
"""
from app import crear_app
from app.core.extensions import db
from app.models import Usuario

app = crear_app()

with app.app_context():
    print("🔧 Creando usuario administrador...")
    
    # Verificar si ya existe
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
        db.session.commit()
        print("✅ Usuario admin creado exitosamente!")
        print("\n📝 Credenciales de acceso:")
        print("   Email: admin@inventario.com")
        print("   Password: admin123")
    else:
        print("ℹ️  Usuario admin ya existe")
        print("\n📝 Credenciales de acceso:")
        print("   Email: admin@inventario.com")
        print("   Password: admin123")
    
    print("\n🌐 Accede al sistema en: http://localhost:3000")
