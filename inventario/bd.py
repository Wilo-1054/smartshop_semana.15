from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ProductoORM(db.Model):
    __tablename__ = 'productos_orm'

    id       = db.Column(db.Integer, primary_key=True)
    nombre   = db.Column(db.String(120), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=0)
    precio   = db.Column(db.Float, nullable=False, default=0.0)

    def __repr__(self):
        return f'<ProductoORM {self.nombre}>'
