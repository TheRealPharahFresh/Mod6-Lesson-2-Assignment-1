from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
import mysql.connector
from mysql.connector import Error



app = Flask(__name__)
ma = Marshmallow(app)


class MemberSchema(ma.Schema):
    id = fields.String(required=True)
    name = fields.String(required=True)
    age = fields.String(required=True)

    class Meta:
        fields = ("id", "name", "age")

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)


class WorkoutSessionSchema(ma.Schema):
    id = fields.String(required=True)
    date = fields.Date(required=True)
    duration_minutes = fields.String(required=True)  # Duration in minutes
    calories_burned = fields.String(required=True)
    member_id = fields.String(required=True)

    class Meta:
        fields = ("id", "date", "duration_minutes", "calories_burned", "member_id")

workout_session_schema = WorkoutSessionSchema()
workout_sessions_schema = WorkoutSessionSchema(many=True)






def get_db_connection():

    db_name = "FitnessCenter"
    user = "root"
    password = "Godswill150"
    host = "127.0.0.1"

    try:
        conn = mysql.connector.connect(
            database = db_name,
            user = user,
            password = password,
            host = host
        )

        print("Connected To MySQL database successfully!")
        return conn
    except Exception as e:
        print(f"Error: {e}")
        return None
    

@app.route('/')
def home():
    return 'Welcome to the Fitness Center'
@app.route("/members", methods=["GET"])
def get_members():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"Error": "Database Connection Failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM Members"

        cursor.execute(query)
        members = cursor.fetchall()
        return members_schema.jsonify(members)
    except Error as e:
        print(f'Error: {e}')
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()



@app.route("/members", methods=["POST"])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        print(f'Error: {e}')
        return jsonify({e.messages}), 400
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"Error": "Database Connection Failed"}), 500
        cursor = conn.cursor()

        new_member = ( member_data['id'],member_data['name'], member_data['age'])
        query = "INSERT INTO Members  (id,name, age) VALUES (%s,%s,%s)"
        cursor.execute(query,new_member)
        conn.commit()
        return jsonify({"message": "New member added successfully"}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "internal server error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()






@app.route("/members/<int:id>", methods=["PUT"])
def update_member(id):
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"Error": "Database Connection Failed"}), 500
        cursor = conn.cursor()

        updated_member = (member_data['id'], member_data['name'], member_data['age'], id)
        query = "UPDATE Members SET id = %s, name = %s, age = %s WHERE id = %s"
        
        cursor.execute(query, updated_member)
        conn.commit()


       
        return jsonify({"message": "Member updated successfully"}), 201
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()



@app.route("/members/<int:id>", methods=["DELETE"])
def delete_member(id):
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"Error": "Database Connection Failed"}), 500
        cursor = conn.cursor()
        
        member_to_remove = (id,)

        cursor.execute("SELECT * FROM Members where id = %s", member_to_remove)
        customer = cursor.fetchone()
        if not customer:
            return jsonify({"error": "Member not found"}), 404
        
        query = "DELETE FROM Members WHERE id = %s"
        cursor.execute(query, member_to_remove)
        conn.commit()
        
        return jsonify({"message": "Member removed successfully"}), 200
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()



@app.route("/workout-sessions", methods=["GET"])
def get_workout_sessions():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"Error": "Database Connection Failed"}), 500
        cursor = conn.cursor(dictionary=True)

        
        query = "SELECT * FROM WorkoutSessions"
        cursor.execute(query)
        workout_sessions = cursor.fetchall()

    
        return workout_sessions_schema.jsonify(workout_sessions)
    except Error as e:
        print(f'Error: {e}')
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route("/workout-sessions", methods=["POST"])
def schedule_workout_session():
    try:
        
        workout_data = workout_session_schema.load(request.json)
    except ValidationError as e:
        print(f"Validation Error: {e}")
        return jsonify({"errors": e.messages}), 400

    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"Error": "Database Connection Failed"}), 500
        cursor = conn.cursor()

        
        new_session = (
            workout_data['id'],
            workout_data['date'],
            workout_data['duration_minutes'],
            workout_data['calories_burned'],
            workout_data['member_id']
        )
        query = """
            INSERT INTO WorkoutSessions (id, date, duration_minutes, calories_burned, member_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, new_session)
        conn.commit()

        return jsonify({"message": "Workout session scheduled successfully"}), 201
    except Error as e:
        print(f"Database Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/workout-sessions/<int:id>", methods=["PUT"])
def update_workout_session(id):
    try:
        
        workout_data = workout_session_schema.load(request.json)
    except ValidationError as e:
        print(f"Validation Error: {e}")
        return jsonify({"errors": e.messages}), 400

    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"Error": "Database Connection Failed"}), 500
        cursor = conn.cursor()

        
        updated_session = (
            workout_data['date'],
            workout_data['duration_minutes'],
            workout_data['calories_burned'],
            workout_data['member_id'],
            id
        )
        query = """
            UPDATE WorkoutSessions
            SET date = %s, duration_minutes = %s, calories_burned = %s, member_id = %s
            WHERE id = %s
        """
        cursor.execute(query, updated_session)
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Workout session not found"}), 404

        return jsonify({"message": "Workout session updated successfully"}), 200
    except Error as e:
        print(f"Database Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


if __name__ == "__main__":
    app.run(debug=True)