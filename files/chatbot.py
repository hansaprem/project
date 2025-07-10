from flask import Blueprint, request, jsonify
import MySQLdb
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

chatbot_bp = Blueprint('chatbot_bp', __name__)

db = MySQLdb.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB
)
cursor = db.cursor()

@chatbot_bp.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    msg = data.get('message', '').lower()

    try:
        if "present today" in msg:
            cursor.execute("SELECT COUNT(*) FROM attendance WHERE DATE(sign_in) = CURDATE()")
            count = cursor.fetchone()[0]
            reply = f"{count} employees are present today."

        elif "absent today" in msg:
            cursor.execute("""
                SELECT COUNT(*) FROM employees
                WHERE id NOT IN (
                    SELECT employee_id FROM attendance WHERE DATE(sign_in) = CURDATE()
                )
            """)
            count = cursor.fetchone()[0]
            reply = f"{count} employees are absent today."

        elif "how many employees" in msg or "total employees" in msg:
            cursor.execute("SELECT COUNT(*) FROM employees")
            count = cursor.fetchone()[0]
            reply = f"There are {count} total employees."

        elif "list all" in msg or "show all employees" in msg:
            cursor.execute("SELECT name FROM employees")
            names = [row[0] for row in cursor.fetchall()]
            reply = "Employees: " + ", ".join(names)

        elif "male" in msg and "female" in msg:
            cursor.execute("SELECT gender, COUNT(*) FROM employees GROUP BY gender")
            genders = cursor.fetchall()
            gender_stats = ", ".join([f"{g[0]}: {g[1]}" for g in genders])
            reply = f"Gender stats → {gender_stats}"

        elif "most present" in msg or "highest attendance" in msg:
            cursor.execute("""
                SELECT e.name, COUNT(a.id) as attendance_days 
                FROM attendance a
                JOIN employees e ON e.id = a.employee_id
                GROUP BY a.employee_id
                ORDER BY attendance_days DESC
                LIMIT 1
            """)
            result = cursor.fetchone()
            if result:
                reply = f"The employee with highest attendance is {result[0]} with {result[1]} days."
            else:
                reply = "No attendance data found."

        elif "least present" in msg or "lowest attendance" in msg:
            cursor.execute("""
                SELECT e.name, COUNT(a.id) as attendance_days 
                FROM employees e
                LEFT JOIN attendance a ON e.id = a.employee_id
                GROUP BY e.id
                ORDER BY attendance_days ASC
                LIMIT 1
            """)
            result = cursor.fetchone()
            reply = f"The employee with lowest attendance is {result[0]} with {result[1]} days."

        elif "city wise" in msg or "by city" in msg:
            cursor.execute("SELECT city, COUNT(*) FROM employees GROUP BY city")
            rows = cursor.fetchall()
            reply = "\n".join([f"{city}: {count}" for city, count in rows])

        elif "help" in msg or "what can you do" in msg:
            reply = (
                "You can ask me:\n"
                "- How many employees are present today?\n"
                "- Who is absent today?\n"
                "- Show all employees\n"
                "- How many male and female employees?\n"
                "- Employee with highest or lowest attendance\n"
                "- Employees by city"
            )

        else:
            reply = "Sorry, I didn't understand that. Try asking something like 'How many employees are present today?' or type 'help'."

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})
