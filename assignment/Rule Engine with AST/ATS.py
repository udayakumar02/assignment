import ast
from collections import Counter
import sqlite3
import os
from flask import Flask, render_template

DB_PATH = os.path.abspath('rules.db')

app = Flask(__name__)

class Database:
    """Singleton class to manage database connection."""
    _connection = None

    @classmethod
    def get_connection(cls):
        """Get or create a new connection."""
        if cls._connection is None:
            cls._connection = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
        return cls._connection

    @classmethod
    def close_connection(cls):
        """Close the connection if it exists."""
        if cls._connection:
            cls._connection.close()
            cls._connection = None

def fetch_rules():
    """Fetch and return all rules from the database."""
    rules_list = []
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM rules;")
        rules = cursor.fetchall()

        for rule in rules:
            rule_info = {
                'id': rule[0],
                'rule_string': rule[1],
                'created_at': rule[2],
                'nodes': []
            }

            cursor.execute("SELECT * FROM nodes WHERE rule_id = ?;", (rule[0],))
            nodes = cursor.fetchall()
            for node in nodes:
                rule_info['nodes'].append({
                    'id': node[0],
                    'type': node[2],
                    'value': node[5],
                    'left_node': node[3],
                    'right_node': node[4]
                })

            rules_list.append(rule_info)

    except sqlite3.Error as e:
        print(f"Database error during fetching: {e}")
    finally:
        Database.close_connection()

    return rules_list

@app.route('/')
def index():
    rules = fetch_rules()
    return render_template('index.html', rules=rules)

if __name__ == '__main__':
    app.run(debug=True)
