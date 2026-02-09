from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import URL, ExceptionContext
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import json

app = Flask(__name__)

# Classe base para construcao de outras classes
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

ex = ExceptionContext() # Objeto que retorna erros relacionados ao SQLAlchemy

# Cria a tabela users no banco de dados
class Users(db.Model):

	id_user : Mapped[int] = mapped_column(primary_key=True, unique=True)
	username : Mapped[str] = mapped_column(nullable=False, unique=True)
	user_admin : Mapped[bool] = mapped_column(nullable=False)

	# Converte os dados para um dicionario para depois converte-los em JSON com o metodo .jsonify()

	def convert_dict(self):
		return {
			"id_user": self.id_user,
			"username": self.username,
			"user_admin": self.user_admin
		}

# Pega o arquivo secrets em JSON, extrai e retorna seus dados 
def get_json(secrets_json, key):
        try:
            with open(secrets_json) as s:
                data = json.load(s)
                return data[key]
        except Exception as e:
            print("Error: ", e)
            
url_conn = get_json("secrets.json", "db")

url_obj = URL.create(
	url_conn['dialect'],
	username=url_conn['username'],
 	password=url_conn['password'],
	host=url_conn['host'],
 	port=int(url_conn['port']),
	database=url_conn['database']
)

#Cria a conexao para o banco de dados
app.config["SQLALCHEMY_DATABASE_URI"] = url_obj

db.init_app(app)

#Cria routes/rotas
@app.route("/")
def home():
	return "Index"

@app.route("/hello")
def hello():
	return jsonify({"message": "hello"})

# Lista os usuarios
@app.route("/users", methods=["GET"])
def users_list():
	users = db.session.execute(db.select(Users).order_by(Users.id_user)).scalars() # Executa como se fosse um SELECT na tabela
 
	return jsonify([u.convert_dict() for u in users]) # Retorna os dados convertidos em JSON

# Cria usuarios novos
@app.route("/add_user", methods=["POST"])
def user_add():
	data = request.get_json()

	users = db.session.execute(db.select(Users).order_by(Users.id_user)).scalars()
	usr = [u.convert_dict() for u in users]

	novo_user = Users(
			username=data["username"],
			user_admin=data["user_admin"]
		)

	usernames = [i["username"] for i in usr]

	if novo_user.username in usernames:
		return jsonify({"error": "Usuario ja existe."}), 404
	elif novo_user.user_admin == None:
		return jsonify({"error": "'user_admin' nao pode ser nulo."}), 404
	elif novo_user.username == "" or None:
		return jsonify({"error": "'username' nao pode ser nulo."}), 404
	elif " " in novo_user.username:
		return jsonify({"error": "nao pode haver '<space>' em 'username'"}), 404
	else:
		db.session.add(novo_user)
		db.session.commit()

	return jsonify(novo_user.convert_dict()), 201
	

# Lista usuarios pelo id_user
@app.route("/list_user", methods=["GET"])
def list_user():
	data = request.get_json()

	try:
		user = db.session.execute(db.select(Users).where(Users.id_user == data['id_user'])).scalar_one()        
		if user:
			return user.convert_dict()
	except:
		return jsonify({"error: " : "Usuario nao existe"}), 404

# Modifica usuarios
@app.route("/update_user", methods=["PUT"])
def update_user():
    data = request.get_json()
    
    users = db.session.execute(db.select(Users).order_by(Users.id_user)).scalars()
    usr = [u.convert_dict() for u in users]
    usernames = [i['username'] for i in usr]
    
    user = db.session.execute(db.select(Users).where(Users.id_user == data['id_user'])).scalar_one()
    user_dict = user.convert_dict()
    
    if user_dict:
        user.id_user = data.get("id_user", user.id_user)
        user.username = data.get("username", user.username)
        user.user_admin = data.get("user_admin", user.user_admin)
        
        if user.id_user != data.get("id_user", user.id_user) and data.get("username", user.username) in usernames:
            return jsonify({"error :" : "'username' ja existe. Coloque outro valor."}), 404
        elif data.get("username", user.username) == "" or None:
            return jsonify({"error :" : "'username' nao pode ser nulo."}), 404
        elif data.get("user_admin", user.user_admin):
            db.session.commit()
            return "Usuario modificado!", 201
        else:            
            db.session.commit()
            return "Usuario modificado!", 201
    else:
        return jsonify({"error: " : "Usuario nao existe"}), 404
  
# Deleta usuarios
@app.route("/delete_user", methods=["DELETE"])
def delete_user():
    data = request.get_json()
    
    try:
        user = db.session.execute(db.select(Users).where(Users.id_user == data['id_user'])).scalar_one()
        if user:
         db.session.delete(user)
         db.session.commit()
         return jsonify({"message": "Usuario deletado."}), 201
    except:
        return jsonify({"error": "Usuario nao existe."}), 404


if __name__ == "__main__":
	app.run(debug=False)
