import mysql.connector
from mysql.connector import Error

try:
    connection = mysql.connector.connect(
        host='localhost',
        database='WSP_System',
        user='root',
        password='awsp3142'
    )
    
    if connection.is_connected():
        cursor = connection.cursor(dictionary=True)
        
        # Test query
        cursor.execute("SELECT COUNT(*) as count FROM Officer")
        result = cursor.fetchone()
        print(f"✅ DB Connected! Officers in system: {result['count']}")
        
        # List officers
        cursor.execute("SELECT Badge_Number, First_Name, Last_Name FROM Officer")
        officers = cursor.fetchall()
        for officer in officers:
            print(f"  - {officer['Badge_Number']}: {officer['First_Name']} {officer['Last_Name']}")
        
        cursor.close()
        connection.close()
        
except Error as e:
    print(f"❌ DB Connection Failed: {e}")
