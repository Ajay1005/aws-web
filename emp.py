from flask import Flask, render_template, request
import pymysql
import boto3
from config import *

emp = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = pymysql.connect(host=customhost, port=3306, user=customuser, password=custompass, db=customdb)
output = {}
table = 'employee'


@emp.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')


@emp.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')

@emp.route("/getemp", methods=['GET', 'POST'])
def getempp():
    return render_template('GetEmp.html')

#@emp.route("/fetchdata", methods=['GET', 'POST'])
#def fetch():
    #emp_id = request.form['emp_id']
    #sql_query = select * from 'employee' where 'empid'=1
    #cursor = db_conn.cursor()
    #cursor.execute(sql_query)
    #record=cursor.fetchone()
    #return render_template('GetEmpOutput.html', id=record[0], fname=record[1], lname=record[2], interest=record[3], location=record[4])"""




@emp.route("/addemp", methods=['GET', 'POST'])
def addemp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:
        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(s3_location, custombucket, emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)


if __name__ == '__main__':
    emp.run(host='0.0.0.0', port=80, debug=True)
