from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
from mysql_connector import MySQLConnector, Error

app = Flask(__name__)
ma = Marshmallow(app)
my_sql_connector = MySQLConnector()

class MemberSchema(ma.Schema):
    name = fields.String(required=True)
    age = fields.Integer(required=True)

    class Meta:
        fields = ("name", "age")

class WorkoutSessionSchema(ma.Schema):
    member_id = fields.Integer(required=True)
    session_date = fields.Date(required=True)
    session_time = fields.String(required=True)
    activity = fields.String(required=True)

    class Meta:
        fields = ("member_id", "session_date", "session_time", "activity")

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)
workout_session_schema = WorkoutSessionSchema()
workout_sessions_schema = WorkoutSessionSchema(many=True)

# Task 2: Implementing CRUD Operations for Members

@app.route("/")
def home():
    return "Welcome to the fitness_center_db Flask application!"

@app.route("/members", methods=["GET"])
def get_members():
    try:
        conn = my_sql_connector.get_db_connection()

        if not conn:
            return jsonify({"error": "Database connection failed."}), 500
        
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM Members;"

        cursor.execute(query)

        members = cursor.fetchall()

        return members_schema.jsonify(members)
    except Error as e:
        print(f"Error: {e}.")

        return jsonify({"error": "Internal server error."}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/members", methods=["POST"])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}.")

        return jsonify(e.messages), 400
    
    try:
        conn = my_sql_connector.get_db_connection()

        if not conn:
            return jsonify({"error": "Database connection failed."}), 500
        
        cursor = conn.cursor()
        new_member = (member_data["name"], member_data["age"])
        query = """
        INSERT INTO Members (name, age)
        VALUES (%s, %s);
        """

        cursor.execute(query, new_member)
        conn.commit()

        return jsonify({"message": "New member added successfully!"}), 201
    except Error as e:
        print(f"Error: {e}.")

        return jsonify({"error": "Internal server error."}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/members/<int:id>", methods=["PUT"])
def update_member(id):
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}.")

        return jsonify(e.messages), 400
    
    try:
        conn = my_sql_connector.get_db_connection()

        if not conn:
            return jsonify({"error": "Database connection failed."}), 500
        
        cursor = conn.cursor()
        updated_member = (member_data["name"], member_data["age"], id)
        query = """
        UPDATE Members
        SET name = %s, age = %s
        WHERE id = %s;
        """

        cursor.execute(query, updated_member)
        conn.commit()

        return jsonify({"message": "Member updated successfully!"}), 200
    except Error as e:
        print(f"Error: {e}.")

        return jsonify({"error": "Internal server error."}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/members/<int:id>", methods=["DELETE"])
def delete_member(id):
    try:
        conn = my_sql_connector.get_db_connection()

        if not conn:
            return jsonify({"error": "Database connection failed."}), 500
        
        cursor = conn.cursor()
        member_to_remove = (id,)

        cursor.execute("SELECT * FROM Members WHERE id = %s;", member_to_remove)

        if not cursor.fetchone():
            return jsonify({"error": "Member not found."}), 404
        
        query = """
        DELETE FROM Members
        WHERE id = %s;
        """

        cursor.execute(query, member_to_remove)
        conn.commit()

        return jsonify({"message": "Member removed successfully!"}), 200
    except Error as e:
        print(f"Error: {e}.")

        return jsonify({"error": "Internal server error."}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Task 3: Managing Workout Sessions

@app.route("/workout_sessions", methods=["GET"])
def get_workout_sessions():
    try:
        conn = my_sql_connector.get_db_connection()

        if not conn:
            return jsonify({"error": "Database connection failed."}), 500
        
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM WorkoutSessions;"

        cursor.execute(query)

        workout_sessions = cursor.fetchall()

        return workout_sessions_schema.jsonify(workout_sessions)
    except Error as e:
        print(f"Error: {e}.")

        return jsonify({"error": "Internal server error."}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/workout_sessions/<int:id>", methods=["GET"])
def get_workout_session(id):
    try:
        conn = my_sql_connector.get_db_connection()

        if not conn:
            return jsonify({"error": "Database connection failed."}), 500
        
        cursor = conn.cursor(dictionary=True)
        session_id = (id,)
        query = """SELECT * FROM WorkoutSessions
        WHERE session_id = %s;"""

        cursor.execute(query, session_id)

        workout_session = cursor.fetchone()

        if not workout_session:
            return jsonify({"error": "Workout session not found."}), 404

        return workout_session_schema.jsonify(workout_session)
    except Error as e:
        print(f"Error: {e}.")

        return jsonify({"error": "Internal server error."}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/workout_sessions", methods=["POST"])
def add_workout_session():
    try:
        workout_session_data = workout_session_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}.")

        return jsonify(e.messages), 400
    
    try:
        conn = my_sql_connector.get_db_connection()

        if not conn:
            return jsonify({"error": "Database connection failed."}), 500
        
        cursor = conn.cursor()
        new_workout_session = (workout_session_data["member_id"],
        workout_session_data["session_date"], 
        workout_session_data["session_time"],
        workout_session_data["activity"])
        query = """
        INSERT INTO WorkoutSessions (member_id, session_date, session_time, activity)
        VALUES (%s, %s, %s, %s);
        """

        cursor.execute("SELECT id FROM Members;")

        if workout_session_data["member_id"] not in cursor.fetchall()[0]:
            return jsonify({"error": "Member not found."}), 404

        cursor.execute(query, new_workout_session)
        conn.commit()

        return jsonify({"message": "New workout session added successfully!"}), 201
    except Error as e:
        print(f"Error: {e}.")

        return jsonify({"error": "Internal server error."}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/workout_sessions/<int:id>", methods=["PUT"])
def update_workout_session(id):
    try:
        workout_session_data = workout_session_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}.")

        return jsonify(e.messages), 400
    
    try:
        conn = my_sql_connector.get_db_connection()

        if not conn:
            return jsonify({"error": "Database connection failed."}), 500
        
        cursor = conn.cursor()
        updated_workout_session = (workout_session_data["member_id"],
        workout_session_data["session_date"], 
        workout_session_data["session_time"],
        workout_session_data["activity"],
        id)
        query = """
        UPDATE WorkoutSessions
        SET member_id = %s, session_date = %s, session_time = %s, activity = %s
        WHERE session_id = %s;
        """

        cursor.execute("SELECT id FROM Members;")

        if workout_session_data["member_id"] not in cursor.fetchall()[0]:
            return jsonify({"error": "Member not found."}), 404

        cursor.execute(query, updated_workout_session)
        conn.commit()

        return jsonify({"message": "Workout session updated successfully!"}), 200
    except Error as e:
        print(f"Error: {e}.")

        return jsonify({"error": "Internal server error."}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/workout_sessions/<int:id>", methods=["DELETE"])
def delete_workout_session(id):
    try:
        conn = my_sql_connector.get_db_connection()

        if not conn:
            return jsonify({"error": "Database connection failed."}), 500
        
        cursor = conn.cursor()
        workout_session_to_remove = (id,)

        cursor.execute("SELECT * FROM WorkoutSessions WHERE member_id = %s;", workout_session_to_remove)

        if not cursor.fetchone():
            return jsonify({"error": "Member not found."}), 404
        
        query = """
        DELETE FROM WorkoutSessions
        WHERE session_id = %s;
        """

        cursor.execute(query, workout_session_to_remove)
        conn.commit()

        return jsonify({"message": "Workout session removed successfully!"}), 200
    except Error as e:
        print(f"Error: {e}.")

        return jsonify({"error": "Internal server error."}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()