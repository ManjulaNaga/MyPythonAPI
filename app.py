import argparse
import json
import requests
# import response
from influxdb import InfluxDBClient
from flask import Flask, jsonify, request, Response, render_template
from flask_restful import Api, Resource, reqparse
from functools import wraps
import logging

app = Flask(__name__)

# 'logging function' decorator definition


def logged(func):
    @wraps(func)
    def with_logging(*args, **kwargs):
        print(func.__name__ + " was called")
        return func(*args, **kwargs)
    return with_logging


# class decorator definition
class InvalidUsage(Exception):
    status_code = 400  # defaulty set status to 400

    # contructor method definition
    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    # dictionary format the payload
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@logged  # using logged decorator
@app.errorhandler(InvalidUsage)  # using InvalidUsage decorator class
# function definition with error message as parameter
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())  # convert error to json format
    response.status_code = error.status_code
    return response     # return error message


@logged  # using logged decorator
def main(host='localhost', port=8086):
    """Instantiate a connection to the InfluxDB."""
    logging.basicConfig(filename='myapp.log', level=logging.INFO)
    logging.info("started logging...")
    user = 'manju'
    password = 'manju'
    dbname = 'userdb'
    dbuser = 'manju'

    global client
    client = InfluxDBClient(host, port, user, password, dbname)


print(main.__name__)
print(main.__doc__)


@logged  # using logged decorator
def parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(
        description='example code to play with InfluxDB')
    parser.add_argument('--host', type=str, required=False,
                        default='localhost',
                        help='hostname of InfluxDB http API')
    parser.add_argument('--port', type=int, required=False, default=8086,
                        help='port of InfluxDB http API')
    return parser.parse_args()


# @logged  # using logged decorator
@app.route("/user/", methods=["GET"])  # fetch names of  all users
def get_users():
    """
    This function lists all users.
    """
    # get _all_ the users
    results = client.query("SELECT * from user_role")
    points = results.get_points()  # fetch data from influxDB
    logging.info("printing items........")
    nameList = []
    for item in points:
        print(item['name'])  # fetch the name fields of the measurement
        nameList.append(item['name'])  # append the names to the list
    logging.info("Finished")
    return json.dumps(nameList)  # return the  list


print(get_users.__name__)
print(get_users.__doc__)


@logged  # using logged decorator
@app.route("/user/<string:user_id>", methods=["GET"])
def get_user(user_id):
    """
    This function displays a particular user.
    :param user_id: user ID
    :type user_id: int
    """
    logging.info("get user function is working....")
    # display a particular users
    nameList = []
    results = client.query("SELECT * from user_role where id =\'"+user_id+"\'")
    points = results.get_points()  # fetch data from influxDB
    print("SELECT * from user_role where id =\'"+user_id+"\'")
    print("printing item with id........"+str(user_id))
    for item in points:  # iterate through all data points with given  user_id
        # fetch the name field of the measurement with given  user_id
        print(item['name'])
        nameList.append(item)  # append the names to the list

    logging.info("get user function is ended....")
    return json.dumps(nameList)  # return the  list


print(get_user.__name__)
print(get_user.__doc__)


@logged  # using logged decorator
@app.route("/user", methods=["POST"])  # Post method call
def post_user():
    """
    This function disposts details of particular user.

    """
    # get the authToken from the API request
    header_value = request.headers.get('authToken')
    print(header_value)

    if header_value == "py-influx-assignment":  # validate the header auth token value

        req_data = request.json  # if successful, fetch data from the request
        print(req_data['fields'])
        user_id = req_data['fields']['id']
        name = req_data['fields']['name']
        role = req_data['fields']['role']

        return '''
            The user id value is: {}
            The name value is: {}
            The role version is: {}'''.format(user_id, name, role)
    elif header_value == '':  # if header suth token value is empty, raise exception
        raise InvalidUsage('header is missing', status_code=401)
    else:  # if header suth token value is incorrect, raise exception
        raise InvalidUsage('header is invalid', status_code=500)


print(post_user.__name__)
print(post_user.__doc__)

if __name__ == '__main__':
    args = parse_args()
    main(host=args.host, port=args.port)
    # api.add_resource(User, "/user/<string:name>")
app.run(debug=True)
