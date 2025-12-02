from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

app = Flask(__name__)

#Configura dados de acesso do banco
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@localhost:5432/banco_apipython"

#Cria o objeto banco de dados
db = SQLAlchemy(app)

#Cria a tabela users no banco de dados
class Users(db.Model):
	id_user : Mapped[int] = mapped_column(primary_key=True)
	username : Mapped[str] = mapped_column(nullable=False)
	user_admin : Mapped[bool] = mapped_column(nullable=False)

	# Necessario converter os dados para JSON

	def convert_dict(self):
		return {
			"id_user": self.id_user,
			"username": self.username,
			"user_admin": self.user_admin
		}

with app.app_context():
	db.create_all()

#Cria routes/rotas
@app.route("/")
def home():
	return "Index"

@app.route("/hello")
def hello():
	return jsonify({"message": "hello"})

# Lista os usuarios
@app.route("/users", methods=["GET"])
def list_users():
	users = Users.query.all() # Executa como se fosse um SELECT na tabela
	
	return jsonify([users.convert_dict()] for u in users)


# Cria usuarios novos
@app.route("/add_user", methods=["POST"])
def user_add():
	data = request.get_json()

	novo_user = Users(
			username=data["username"],
			user_admin=data["user_admin"]
		)

	db.session.add(novo_user)
	db.session.commit()

	return jsonify(novo_user.convert_dict()), 201



if __name__ == "__main__":
	app.run(debug=True)
