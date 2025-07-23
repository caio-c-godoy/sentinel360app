from models import db, User
from app import app

with app.app_context():
    # Verifica se já existe um usuário admin
    if User.query.filter_by(email="admin@admin.com").first():
        print("Usuário admin já existe.")
    else:
        admin = User(
            nome="Admin",
            email="admin@admin.com",
            permissoes="admin",
            is_admin=True,
            can_view=True,
            can_create=True,
            can_edit=True,
            can_delete=True,
            can_export=True
        )
        admin.set_password("mirinda@1q2w3e")  # Define a senha com hash
        db.session.add(admin)
        db.session.commit()
        print("Usuário admin criado com sucesso!")
