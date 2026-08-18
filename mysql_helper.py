import pymysql
class MySqlHelper:
    def __init__(self,host,port,user,password,database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
    
    def _get_connection(self):
        conn = pymysql.connect(
            host = self.host,
            port = self.port,
            user = self.user,
            password = self.password,
            database = self.database,
            charset = 'utf8mb4',
            cursorclass = pymysql.cursors.DictCursor
        )
        return conn
    
    def select(self,sql,params=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql,params)
            result = cursor.fetchall()
            return result
        except Exception as e:
            print(f"Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def execute(self,sql,params=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            affected_rows = cursor.execute(sql,params)
            conn.commit()
            return affected_rows
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            return 0
        finally:
            cursor.close()
            conn.close()

def main():
    print("Database Initialization:")
    while True:
        db_password = input("Please enter your local MySQL 'root' password: ")
        try:
            pymysql.connect(host='localhost', port=3306, user='root', password=db_password, database='school').close()
            print("Connection successful!\n")
            break
        except Exception:
            print("Password incorrect or connection failed. Please try again.")
            
    test_db = MySqlHelper('localhost',3306,'root',db_password,'school')

    while True:
        print("Student Information Management System")
        print("1. Add new student")
        print("2. Query all students")
        print("3. Update student height")
        print("4. Delete student record")
        print("5. Delete database")
        print("0. Exit system")
        
        choice = input("Please enter the operation number (0-5): ")

        if choice == '1':
            print("\nChoice Selected: Add New Student")
            stu_id = input("Enter student ID: ")
            
            check_sql = "SELECT * FROM student WHERE stu_id = %s"
            existing_student = test_db.select(check_sql, (stu_id,))
            
            if existing_student:
                print(f"Add failed: Student ID '{stu_id}' already exists!")
            else:
                name = input("Enter student name: ")
                raw_height = input("Enter student height (e.g., 175.5): ")
                
                try:
                    height_float = float(raw_height)
                    formatted_height = f"{height_float:.2f}"
                except ValueError:
                    print("Error: Invalid height format! Please enter valid numbers only.")
                    continue
                
                sql = "INSERT INTO student (stu_id, name, height) VALUES (%s, %s, %s)"
                rows = test_db.execute(sql, (stu_id, name, formatted_height))
                
                if rows > 0:
                    print(f"Successfully added! Affected rows: {rows} (Height saved as: {formatted_height})")
                else:
                    print(f"Add failed: Something went wrong during database execution.")
            
        elif choice == '2':
            print("\nChoice Selected: Query All Students")
            sql = "SELECT * FROM student"
            students = test_db.select(sql)
            if not students:
                print("The system currently has no student data.")
            else:
                for s in students:
                    print(f"ID: {s['stu_id']} | Name: {s['name']} | Height: {s['height']}cm")

        elif choice == '3':
            print("\nChoice Selected: Update Student Height")
            name = input("Enter the name of the student to update: ")
            raw_new_height = input("Enter the new height: ")
            
            try:
                height_float = float(raw_new_height)
                formatted_new_height = f"{height_float:.2f}"
            except ValueError:
                print("Error: Invalid height format! Please enter valid numbers only.")
                continue
            
            sql = "UPDATE student SET height = %s WHERE name = %s"
            rows = test_db.execute(sql, (formatted_new_height, name))
            
            if rows > 0:
                print(f"Successfully updated! Affected rows: {rows} (New height saved as: {formatted_new_height})")
            else:
                print("Update failed. Student name might not exist.")

        elif choice == '4':
            print("\nChoice Selected: Delete Student Record")
            stu_id = input("Enter the ID of the student to delete: ")
            
            confirm = input(f"Are you sure you want to delete the student with ID {stu_id}? (Enter 'y' to confirm, any other key to cancel): ")
            if confirm.lower() == 'y':
                sql = "DELETE FROM student WHERE stu_id = %s"
                rows = test_db.execute(sql, (stu_id,))
                if rows > 0:
                    print("Successfully deleted!")
                else:
                    print("Delete failed. Student ID might not exist.")
            else:
                print("Delete operation cancelled.")

        elif choice == '5':
            print("\nChoice Selected: Delete database(This will end the system)")
            confirm = input(f"Are you sure you want to delete the DATABASE? (Enter 'y' to confirm, any other key to cancel): ")
            if confirm.lower() == 'y':
                sql = "DROP DATABASE IF EXISTS school"
                test_db.execute(sql)
                print("Database deleted.")
                break
            else:
                print("Delete database failed.")
                break

        elif choice == '0':
            print("\nThank you for using the system.")
            break

        else:
            print("\nError: Invalid option. Please enter a number between 0 and 5.")

def test_mysql_helper():
    print("Start Database Connection")
    db_password = input("Enter local MySQL 'root' password for testing: ")
    test_db = MySqlHelper('localhost', 3306, 'root', db_password, 'school')
    
    print("\nStarting Unit Tests")

    #Test 1: Test EXECUTE method
    print("\n[Test 1] Verify execute method: Insert")
    test_stu_id = "TEST999"
    
    #Initialize: Clean up existing test data to prevent errors
    test_db.execute("DELETE FROM student WHERE stu_id = %s", (test_stu_id,))
    
    #1. Test Input
    insert_sql = "INSERT INTO student (stu_id, name, height) VALUES (%s, %s, %s)"
    insert_params = (test_stu_id, 'AutoTestUser', 175.50)
    
    #2. Actual Output
    actual_affected_rows = test_db.execute(insert_sql, insert_params)
    
    #3. Expected Output
    expected_rows = 1
    
    #4. Compare
    if actual_affected_rows == expected_rows:
        print(f"Pass: Actual rows({actual_affected_rows}) == Expected({expected_rows})")
    else:
        print(f"Fail: Actual rows({actual_affected_rows}) != Expected({expected_rows})")

    #Test 2: Test SELECT method
    print("\n[Test 2] Verify SELECT method")
    
    select_sql = "SELECT name, height FROM student WHERE stu_id = %s"
    select_params = (test_stu_id,)
    
    actual_result = test_db.select(select_sql, select_params)
    
    expected_name = 'AutoTestUser'

    if len(actual_result) > 0 and actual_result[0]['name'] == expected_name:
        print(f"Pass: Actual Name({actual_result[0]['name']}) == Expected ({expected_name})")
    else:
        print(f"Fail: Actual result {actual_result} does not match expected name.")

    #Test 3: Test EXECUTE method
    print("\n[Test 3] Verify EXECUTE method (Using Delete)")

    delete_sql = "DELETE FROM student WHERE stu_id = %s"
    delete_params = (test_stu_id,)
 
    actual_del_rows = test_db.execute(delete_sql, delete_params)

    expected_del_rows = 1

    if actual_del_rows == expected_del_rows:
        print(f"Pass: Actual deleted rows({actual_del_rows}) == Expected({expected_del_rows})")
    else:
        print(f"Fail: Actual deleted rows({actual_del_rows}) != Expected({expected_del_rows})")

    print("\nUnit Tests Completed")

if __name__ == '__main__':
    test_mysql_helper()
