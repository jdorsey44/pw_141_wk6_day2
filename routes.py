
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = generate_password_hash(data['password'])
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity={'username': user.username})
        return jsonify(access_token=access_token)
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/items', methods=['GET', 'POST'])
@jwt_required()
def items():
    if request.method == 'GET':
        items = Item.query.all()
        result = [{'id': item.id, 'name': item.name, 'description': item.description, 'tags': [{'id': tag.id, 'name': tag.name} for tag in item.tags]} for item in items]
        return jsonify(result)
    elif request.method == 'POST':
        data = request.json
        new_item = Item(name=data['name'], description=data['description'])
        db.session.add(new_item)
        db.session.commit()
        for tag_name in data.get('tags', []):
            new_tag = Tag(name=tag_name, item_id=new_item.id)
            db.session.add(new_tag)
        db.session.commit()
        return jsonify({'message': 'Item created successfully'}), 201

@app.route('/items/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def single_item(item_id):
    item = Item.query.get_or_404(item_id)
    if request.method == 'GET':
        return jsonify({'id': item.id, 'name': item.name, 'description': item.description, 'tags': [{'id': tag.id, 'name': tag.name} for tag in item.tags]})
    elif request.method == 'PUT':
        data = request.json
        item.name = data.get('name', item.name)
        item.description = data.get('description', item.description)
        db.session.commit()
        existing_tag_ids = [tag.id for tag in item.tags]
        new_tag_ids = []
        for tag_data in data.get('tags', []):
            tag = Tag.query.get(tag_data['id'])
            if tag:
                tag.name = tag_data['name']
                new_tag_ids.append(tag.id)
            else:
                new_tag = Tag(name=tag_data['name'], item_id=item.id)
                db.session.add(new_tag)
                db.session.commit()
                new_tag_ids.append(new_tag.id)
        for tag_id in set(existing_tag_ids) - set(new_tag_ids):
            Tag.query.filter_by(id=tag_id).delete()
        db.session.commit()
        return jsonify({'message': 'Item updated successfully'})
    elif request.method == 'DELETE':
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Item deleted successfully'})
