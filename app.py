from fastapi import FastAPI
from mangum import Mangum
import boto3
import os
from pydantic import BaseModel
import random
import string
import urllib.parse

app = FastAPI()
handler = Mangum(app)
rds_client = boto3.client('rds-data', region_name = 'us-west-1')

class Student(BaseModel):
    username: str
    password: str
    subject: str
    email: str
    address: str

class Teacher(BaseModel):
    username: str
    password: str
    subject: str
    email: str

class Donator(BaseModel):
    username: str
    password: str
    email: str

class Donation(BaseModel):
    title: str
    username: str
    description: str
    subject: str

def execute(sql, type = 'GET', args = []):
    response = rds_client.execute_statement(
        secretArn = os.environ.get('db_credentials_secrets_store_arn'),
        database = os.environ.get('database_name'),
        resourceArn = os.environ.get('db_cluster_arn'),
        sql = sql,
        parameters = args
    )
    
    if type in ['POST', 'UPDATE', 'DELETE']:
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return {'status': 'success'}  
        else:
            return {'status': 'error', 'message': 'could modify into database'}

    elif type == 'GET':
        return response['records']

    return {'status': 'error', 'message': 'invalid type'}

@app.get('/')
async def root():
    return {'status': 'success'}

@app.post('/post-student')
async def post_student(student: Student):
    if execute(f'SELECT * FROM student WHERE username = \'{student.username}\''):
        return {'status': 'error', 'message': 'Username already exists'}
    
    args = [
        {'name': 'username', 'value': {'stringValue': student.username}},
        {'name': 'password', 'value': {'stringValue': student.password}},
        {'name': 'subject', 'value': {'stringValue': student.subject}},
        {'name': 'email', 'value': {'stringValue': student.email}},
        {'name': 'address', 'value': {'stringValue': student.address}},
    ]

    return execute('INSERT INTO student VALUES(:username, :password, :subject, :email, :address)', 'POST', args)
    

@app.post('/post-teacher')
async def post_teacher(teacher: Teacher):
    if execute(f'SELECT * FROM teacher WHERE username = \'{teacher.username}\''):
        return {'status': 'error', 'message': 'Username already exists'}

    args = [
        {'name': 'username', 'value': {'stringValue': teacher.username}},
        {'name': 'password', 'value': {'stringValue': teacher.password}},
        {'name': 'subject', 'value': {'stringValue': teacher.subject}},
        {'name': 'email', 'value': {'stringValue': teacher.email}}
    ]

    return execute('INSERT INTO teacher VALUES(:username, :password, :subject, :email)', 'POST', args)

@app.post('/post-donator')
async def post_donator(donator: Donator):
    if execute(f'SELECT * FROM donator WHERE username = \'{donator.username}\''):
        return {'status': 'error', 'message': 'Username already exists'}

    args = [
        {'name': 'username', 'value': {'stringValue': donator.username}},
        {'name': 'password', 'value': {'stringValue': donator.password}},
        {'name': 'email', 'value': {'stringValue': donator.email}}
    ]

    return execute('INSERT INTO donator VALUES(:username, :password, :email)', 'POST', args)
 
@app.post('/post-donation')
async def post_donation(donation: Donation):
    id = ''.join(random.choices(string.ascii_letters, k = 10))

    while execute(f'SELECT * FROM donation WHERE id = \'{id}\''):
        id = ''.join(random.choices(string.ascii_letters, k = 10))

    args = [
        {'name': 'id', 'value': {'stringValue': id}},
        {'name': 'title', 'value': {'stringValue': donation.title}},
        {'name': 'username', 'value': {'stringValue': donation.username}},
        {'name': 'description', 'value': {'stringValue': donation.description}},
        {'name': 'subject', 'value': {'stringValue': donation.subject}},
    ]

    return execute('INSERT INTO donation VALUES(:id, :title, :username, :description, :subject)', 'POST', args)

@app.get('/get-students')
async def get_students(subject: str):
    subject = urllib.parse.unquote_plus(subject)

    students = []
    result = execute(f'SELECT * FROM student WHERE subject = \'{subject}\'')

    for values in result:
        students.append({
            'username': values[0]['stringValue'],
            'email': values[3]['stringValue']
        })

    return students

@app.get('/get-teachers')
async def get_teachers(subject: str):
    subject = urllib.parse.unquote_plus(subject)

    teachers = []
    result = execute(f'SELECT * FROM teacher WHERE subject = \'{subject}\'')

    for values in result:
        teachers.append({
            'username': values[0]['stringValue'],
            'email': values[3]['stringValue']
        })

    return teachers

@app.get('/get-donations')
async def get_donations(subject: str):
    subject = urllib.parse.unquote_plus(subject)

    donations = []
    result = execute(f'SELECT * FROM donation NATURAL JOIN donator WHERE subject = \'{subject}\'')

    for values in result:
        donations.append({
            'title': values[1]['stringValue'],
            'description': values[2]['stringValue'],
            'email': values[6]['stringValue']
        })

    return donations

@app.get('/login-student')
async def login_student(username: str, password: str):
    response = execute(f'SELECT * FROM student WHERE username = \'{username}\' AND password = \'{password}\'')

    if not response:
        return {'status': 'error', 'messsage': 'username or password is incorrect'}

    student = {
        'subject': response[0][2]['stringValue'],
        'email': response[0][3]['stringValue'],
        'address': response[0][4]['stringValue']
    }

    return {'status': 'success', 'student': student}

@app.get('/login-teacher')
async def login_teacher(username: str, password: str):
    response = execute(f'SELECT * FROM teacher WHERE username = \'{username}\' AND password = \'{password}\'')

    if not response:
        return {'status': 'error', 'messsage': 'username or password is incorrect'}

    teacher = {
        'subject': response[0][2]['stringValue'],
        'email': response[0][3]['stringValue']
    }

    return {'status': 'success', 'teacher': teacher}

@app.get('/login-donator')
async def login_donator(username: str, password: str):
    response = execute(f'SELECT * FROM donator WHERE username = \'{username}\' AND password = \'{password}\'')

    if not response:
        return {'status': 'error', 'messsage': 'username or password is incorrect'}

    donator = {
        'email': response[0][2]['stringValue'],
    }

    return {'status': 'success', 'donator': donator}