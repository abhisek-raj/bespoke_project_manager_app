import sqlite3, json, os
db_path = os.path.join(os.path.dirname(__file__), '..', 'instance', 'db.sqlite')
conn = sqlite3.connect(db_path)
cur = conn.cursor()
try:
    cur.execute('SELECT Employeeid, FirstName, LastName, Email, Password, Role, Admin FROM EMPLOYEE')
    rows = cur.fetchall()
    data = []
    for r in rows:
        data.append({
            'Employeeid': r[0],
            'FirstName': r[1],
            'LastName': r[2],
            'Email': r[3],
            'Password': r[4],
            'Role': r[5],
            'Admin': bool(r[6])
        })
    print(json.dumps(data, indent=2))
except Exception as e:
    print('ERROR:', e)
finally:
    conn.close()
