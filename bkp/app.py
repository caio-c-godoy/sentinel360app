from flask import Flask, render_template, url_for, request, redirect, flash
from models import db, Empresa, TipoSonda, TipoDevice, Product, Location, Sensor, ProductMovement
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)
app.secret_key = '1q2w3e!Q@W#E'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)




class Product(db.Model):

    __tablename__ = 'products'
    product_id      = db.Column(db.String(200), primary_key=True)
    date_created    = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Product %r>' % self.product_id

class Location(db.Model):
    __tablename__   = 'locations'
    location_id     = db.Column(db.String(200), primary_key=True)
    date_created    = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return '<Location %r>' % self.location_id

class ProductMovement(db.Model):

    __tablename__   = 'productmovements'
    movement_id     = db.Column(db.Integer, primary_key=True)
    product_id      = db.Column(db.Integer, db.ForeignKey('products.product_id'))
    qty             = db.Column(db.Integer)
    from_location   = db.Column(db.Integer, db.ForeignKey('locations.location_id'))
    to_location     = db.Column(db.Integer, db.ForeignKey('locations.location_id'))
    movement_time   = db.Column(db.DateTime, default=datetime.utcnow)

    product         = db.relationship('Product', foreign_keys=product_id)
    fromLoc         = db.relationship('Location', foreign_keys=from_location)
    toLoc           = db.relationship('Location', foreign_keys=to_location)
    
    def __repr__(self):
        return '<ProductMovement %r>' % self.movement_id

class Sensor(db.Model):
    __tablename__ = 'sensors'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(100), unique=True, nullable=False)
    empresa = db.Column(db.String(100))
    tipo = db.Column(db.String(50))
    status = db.Column(db.String(50))         # Ex: Em estoque, Em uso, Danificado
    localizacao = db.Column(db.String(100))   # Ex: Cliente, Estoque, Em manutenção
    estoque_minimo = db.Column(db.Integer)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Sensor {self.nome}>'


@app.route('/', methods=["POST", "GET"])
def index():
        
    if (request.method == "POST") and ('product_name' in request.form):
        product_name    = request.form["product_name"]
        new_product     = Product(product_id=product_name)

        try:
            db.session.add(new_product)
            db.session.commit()
            return redirect("/")
        
        except:
            return "There Was an issue while add a new Product"
    
    if (request.method == "POST") and ('location_name' in request.form):
        location_name    = request.form["location_name"]
        new_location     = Location(location_id=location_name)

        try:
            db.session.add(new_location)
            db.session.commit()
            return redirect("/")
        
        except:
            return "There Was an issue while add a new Location"
    else:
        products    = Product.query.order_by(Product.date_created).all()
        locations   = Location.query.order_by(Location.date_created).all()
        return render_template("index.html", products = products, locations = locations)

@app.route('/locations/', methods=["POST", "GET"])
def viewLocation():
    if (request.method == "POST") and ('location_name' in request.form):
        location_name = request.form["location_name"]
        new_location = Location(location_id=location_name)

        try:
            db.session.add(new_location)
            db.session.commit()
            return redirect("/locations/")

        except:
            locations = Location.query.order_by(Location.date_created).all()
            return "There Was an issue while add a new Location"
    else:
        locations = Location.query.order_by(Location.date_created).all()
        return render_template("locations.html", locations=locations)

@app.route('/products/', methods=["POST", "GET"])
def viewProduct():
    if (request.method == "POST") and ('product_name' in request.form):
        product_name = request.form["product_name"]
        new_product = Product(product_id=product_name)

        try:
            db.session.add(new_product)
            db.session.commit()
            return redirect("/products/")

        except:
            products = Product.query.order_by(Product.date_created).all()
            return "There Was an issue while add a new Product"
    else:
        products = Product.query.order_by(Product.date_created).all()
        return render_template("products.html", products=products)

@app.route("/update-product/<name>", methods=["POST", "GET"])
def updateProduct(name):
    product = Product.query.get_or_404(name)
    old_porduct = product.product_id

    if request.method == "POST":
        product.product_id    = request.form['product_name']

        try:
            db.session.commit()
            updateProductInMovements(old_porduct, request.form['product_name'])
            return redirect("/products/")

        except:
            return "There was an issue while updating the Product"
    else:
        return render_template("update-product.html", product=product)

@app.route("/delete-product/<name>")
def deleteProduct(name):
    product_to_delete = Product.query.get_or_404(name)

    try:
        db.session.delete(product_to_delete)
        db.session.commit()
        return redirect("/products/")
    except:
        return "There was an issue while deleteing the Product"

@app.route("/update-location/<name>", methods=["POST", "GET"])
def updateLocation(name):
    location = Location.query.get_or_404(name)
    old_location = location.location_id

    if request.method == "POST":
        location.location_id = request.form['location_name']

        try:
            db.session.commit()
            updateLocationInMovements(
                old_location, request.form['location_name'])
            return redirect("/locations/")

        except:
            return "There was an issue while updating the Location"
    else:
        return render_template("update-location.html", location=location)

@app.route("/delete-location/<name>")
def deleteLocation(id):
    location_to_delete = Location.query.get_or_404(id)

    try:
        db.session.delete(location_to_delete)
        db.session.commit()
        return redirect("/locations/")
    except:
        return "There was an issue while deleteing the Location"

@app.route("/movements/", methods=["POST", "GET"])
def viewMovements():
    if request.method == "POST" :
        product_id      = request.form["productId"]
        qty             = request.form["qty"]
        fromLocation    = request.form["fromLocation"]
        toLocation      = request.form["toLocation"]
        new_movement = ProductMovement(
            product_id=product_id, qty=qty, from_location=fromLocation, to_location=toLocation)

        try:
            db.session.add(new_movement)
            db.session.commit()
            return redirect("/movements/")

        except:
            return "There Was an issue while add a new Movement"
    else:
        products    = Product.query.order_by(Product.date_created).all()
        locations   = Location.query.order_by(Location.date_created).all()
        movs = ProductMovement.query\
        .join(Product, ProductMovement.product_id == Product.product_id)\
        .add_columns(
            ProductMovement.movement_id,
            ProductMovement.qty,
            Product.product_id, 
            ProductMovement.from_location,
            ProductMovement.to_location,
            ProductMovement.movement_time)\
        .all()

        movements   = ProductMovement.query.order_by(
            ProductMovement.movement_time).all()
        return render_template("movements.html", movements=movs, products=products, locations=locations)

@app.route("/update-movement/<int:id>", methods=["POST", "GET"])
def updateMovement(id):

    movement    = ProductMovement.query.get_or_404(id)
    products    = Product.query.order_by(Product.date_created).all()
    locations   = Location.query.order_by(Location.date_created).all()

    if request.method == "POST":
        movement.product_id  = request.form["productId"]
        movement.qty         = request.form["qty"]
        movement.from_location= request.form["fromLocation"]
        movement.to_location  = request.form["toLocation"]

        try:
            db.session.commit()
            return redirect("/movements/")

        except:
            return "There was an issue while updating the Product Movement"
    else:
        return render_template("update-movement.html", movement=movement, locations=locations, products=products)

@app.route("/delete-movement/<int:id>")
def deleteMovement(id):
    movement_to_delete = ProductMovement.query.get_or_404(id)

    try:
        db.session.delete(movement_to_delete)
        db.session.commit()
        return redirect("/movements/")
    except:
        return "There was an issue while deleteing the Prodcut Movement"

@app.route("/product-balance/", methods=["POST", "GET"])
def productBalanceReport():
    movs = ProductMovement.query.\
        join(Product, ProductMovement.product_id == Product.product_id).\
        add_columns(
            Product.product_id, 
            ProductMovement.qty,
            ProductMovement.from_location,
            ProductMovement.to_location,
            ProductMovement.movement_time).\
        order_by(ProductMovement.product_id).\
        order_by(ProductMovement.movement_id).\
        all()
    balancedDict = defaultdict(lambda: defaultdict(dict))
    tempProduct = ''
    for mov in movs:
        row = mov[0]
        if(tempProduct == row.product_id):
            if(row.to_location and not "qty" in balancedDict[row.product_id][row.to_location]):
                balancedDict[row.product_id][row.to_location]["qty"] = 0
            elif (row.from_location and not "qty" in balancedDict[row.product_id][row.from_location]):
                balancedDict[row.product_id][row.from_location]["qty"] = 0
            if (row.to_location and "qty" in balancedDict[row.product_id][row.to_location]):
                balancedDict[row.product_id][row.to_location]["qty"] += row.qty
            if (row.from_location and "qty" in balancedDict[row.product_id][row.from_location]):
                balancedDict[row.product_id][row.from_location]["qty"] -= row.qty
            pass
        else :
            tempProduct = row.product_id
            if(row.to_location and not row.from_location):
                if(balancedDict):
                    balancedDict[row.product_id][row.to_location]["qty"] = row.qty
                else:
                    balancedDict[row.product_id][row.to_location]["qty"] = row.qty

    return render_template("product-balance.html", movements=balancedDict)

@app.route("/movements/get-from-locations/", methods=["POST"])
def getLocations():
    product = request.form["productId"]
    location = request.form["location"]
    locationDict = defaultdict(lambda: defaultdict(dict))
    locations = ProductMovement.query.\
        filter( ProductMovement.product_id == product).\
        filter(ProductMovement.to_location != '').\
        add_columns(ProductMovement.from_location, ProductMovement.to_location, ProductMovement.qty).\
        all()

    for key, location in enumerate(locations):
        if(locationDict[location.to_location] and locationDict[location.to_location]["qty"]):
            locationDict[location.to_location]["qty"] += location.qty
        else:
            locationDict[location.to_location]["qty"] = location.qty

    return locationDict


@app.route("/dub-locations/", methods=["POST", "GET"])
def getDublicate():
    location = request.form["location"]
    locations = Location.query.\
        filter(Location.location_id == location).\
        all()
    print(locations)
    if locations:
        return {"output": False}
    else:
        return {"output": True}

@app.route("/dub-products/", methods=["POST", "GET"])
def getPDublicate():
    product_name = request.form["product_name"]
    products = Product.query.\
        filter(Product.product_id == product_name).\
        all()
    print(products)
    if products:
        return {"output": False}
    else:
        return {"output": True}

@app.route('/sensors', methods=["GET", "POST"])
def sensors():
    if request.method == 'POST':
        nome = request.form['nome']
        codigo = request.form['codigo']
        tipo = request.form['tipo']
        status = request.form['status']
        localizacao = request.form['localizacao']
        empresa = request.form['empresa']

        novo_sensor = Sensor(
            nome=nome,
            codigo=codigo,
            tipo=tipo,
            status=status,
            localizacao=localizacao,
            empresa=empresa
        )

        try:
            db.session.add(novo_sensor)
            db.session.commit()
            flash('Sensor cadastrado com sucesso!', 'success')
            return redirect('/sensors')
        except Exception as e:
            db.session.rollback()
            if 'UNIQUE constraint failed: sensors.codigo' in str(e):
                flash('Erro: já existe um sensor com esse código.', 'danger')
            else:
                flash('Erro ao cadastrar o sensor.', 'danger')

    # FILTROS
    filtro_nome = request.args.get('filtro_nome')
    filtro_tipo = request.args.get('filtro_tipo')
    filtro_status = request.args.get('filtro_status')
    filtro_empresa = request.args.get('filtro_empresa')
    filtro_localizacao = request.args.get('filtro_localizacao')

    query = Sensor.query

    if filtro_nome:
        query = query.filter(Sensor.nome.ilike(f'%{filtro_nome}%'))
    if filtro_tipo:
        query = query.filter(Sensor.tipo.ilike(f'%{filtro_tipo}%'))
    if filtro_status:
        query = query.filter(Sensor.status.ilike(f'%{filtro_status}%'))
    if filtro_empresa:
        query = query.filter(Sensor.empresa.ilike(f'%{filtro_empresa}%'))
    if filtro_localizacao:
        query = query.filter(Sensor.localizacao.ilike(f'%{filtro_localizacao}%'))

    sensores = query.order_by(Sensor.criado_em.desc()).all()

    return render_template('sensors.html', sensores=sensores)
    

@app.route('/delete_sensor/<int:id>', methods=['POST'])
def delete_sensor(id):
    sensor = Sensor.query.get_or_404(id)
    try:
        db.session.delete(sensor)
        db.session.commit()
        flash('Sensor excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir o sensor.', 'danger')
    return redirect('/sensors')


@app.route('/sensors/<int:id>/edit', methods=["GET", "POST"])
def edit_sensor(id):
    sensor = Sensor.query.get_or_404(id)

    if request.method == 'POST':
        sensor.nome = request.form['nome']
        sensor.codigo = request.form['codigo']
        sensor.tipo = request.form['tipo']
        sensor.status = request.form['status']
        sensor.localizacao = request.form['localizacao']
        sensor.empresa = request.form['empresa']

        try:
            db.session.commit()
            flash('Sensor atualizado com sucesso!', 'success')
            return redirect('/sensors')
        except Exception as e:
            db.session.rollback()
            if 'UNIQUE constraint failed: sensors.codigo' in str(e):
                flash('Erro: já existe um sensor com esse código.', 'danger')
            else:
                flash('Erro ao atualizar o sensor.', 'danger')

    return render_template('edit_sensor.html', sensor=sensor)

# ---------------------------
# EMPRESA
# ---------------------------
@app.route('/cadastro/empresa', methods=['GET', 'POST'])
def cadastro_empresa():
    if request.method == 'POST':
        nome = request.form.get('nome')
        if nome:
            nova_empresa = Empresa(nome=nome)
            try:
                db.session.add(nova_empresa)
                db.session.commit()
                flash('Empresa cadastrada com sucesso!', 'success')
            except:
                db.session.rollback()
                flash('Erro ao cadastrar empresa.', 'danger')
        return redirect('/cadastro/empresa')

    empresas = Empresa.query.order_by(Empresa.nome).all()
    return render_template('empresa.html', empresas=empresas)

# ---------------------------
# TIPO DE SONDA
# ---------------------------
@app.route('/cadastro/tipo-sonda', methods=['GET', 'POST'])
def cadastro_tipo_sonda():
    if request.method == 'POST':
        nome = request.form.get('nome')
        if nome:
            nova_sonda = TipoSonda(nome=nome)
            try:
                db.session.add(nova_sonda)
                db.session.commit()
                flash('Tipo de Sonda cadastrado com sucesso!', 'success')
            except:
                db.session.rollback()
                flash('Erro ao cadastrar tipo de sonda.', 'danger')
        return redirect('/cadastro/tipo-sonda')

    sondas = TipoSonda.query.order_by(TipoSonda.nome).all()
    return render_template('tipo_sonda.html', sondas=sondas)

# ---------------------------
# TIPO DE DEVICE
# ---------------------------
@app.route('/cadastro/tipo-device', methods=['GET', 'POST'])
def cadastro_tipo_device():
    if request.method == 'POST':
        nome = request.form.get('nome')
        if nome:
            novo_device = TipoDevice(nome=nome)
            try:
                db.session.add(novo_device)
                db.session.commit()
                flash('Tipo de Device cadastrado com sucesso!', 'success')
            except:
                db.session.rollback()
                flash('Erro ao cadastrar tipo de device.', 'danger')
        return redirect('/cadastro/tipo-device')

    devices = TipoDevice.query.order_by(TipoDevice.nome).all()
    return render_template('tipo_device.html', devices=devices)


def updateLocationInMovements(oldLocation, newLocation):
    movement = ProductMovement.query.filter(ProductMovement.from_location == oldLocation).all()
    movement2 = ProductMovement.query.filter(ProductMovement.to_location == oldLocation).all()
    for mov in movement2:
        mov.to_location = newLocation
    for mov in movement:
        mov.from_location = newLocation
     
    db.session.commit()

def updateProductInMovements(oldProduct, newProduct):
    movement = ProductMovement.query.filter(ProductMovement.product_id == oldProduct).all()
    for mov in movement:
        mov.product_id = newProduct
    
    db.session.commit()

if (__name__ == "__main__"):
    with app.app_context():
        db.create_all()
    app.run(debug=True)

app.config['DEBUG'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True
