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

	# Converte os dados para um dicionario para depois converte-los em JSON com o metodo .jsonify()

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

	return jsonify([u.convert_dict() for u in users]) # Retorna os dados convertidos em JSON


# Cria usuarios novos
@app.route("/add_user", methods=["POST"])
def user_add():
	data = request.get_json()

	users = Users.query.all()
	usr = [u.convert_dict() for u in users]

	novo_user = Users(
			username=data["username"],
			user_admin=data["user_admin"]
		)

	usernames = [i["username"] for i in usr]

	if novo_user.username in usernames:
		return jsonify({"error": "Usuario ja existe."}), 404
	elif novo_user.user_admin == "":
		return jsonify({"error": "'username' nao pode ser nulo."}), 404
	elif novo_user.username == "":
		return jsonify({"error": "'user_admin' nao pode ser nulo."}), 404
	else:
		db.session.add(novo_user)
		db.session.commit()

	return jsonify(novo_user.convert_dict()), 201
	

# Modifica usuarios
@app.route("/users/<int:id_user>", methods=["PUT"])
def update_user(id_user):
	data = request.get_json()

	user = Users.query.get(id_user)
	if user:
		user.username = data.get("username", user.username)
		user.user_admin = data.get("user_admin", user.user_admin)

		db.session.commit()

		return jsonify(user.convert_dict())
	else:
		return jsonify({"error": "Usuario nao existe"}), 404

# Deleta usuarios
@app.route("/users/<int:id_user>", methods=["DELETE"])
def delete_user(id_user):
	user = Users.query.get(id_user)
	if user:
		db.session.delete(user)
		db.session.commit()

		return jsonify({"message": "Usuario deletado."})
	else:
		return jsonify({"error": "Usuario nao existe."}), 404



if __name__ == "__main__":
	app.run(debug=True)
