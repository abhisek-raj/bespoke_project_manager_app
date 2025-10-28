# following this as a guide 
# https://dev.to/nagatodev/how-to-add-login-authentication-to-a-flask-and-react-application-23i7
from flask import Flask, request, jsonify, json, abort
from flask_bcrypt import Bcrypt
from config import ApplicationConfig
from sqlalchemy import or_, and_
from flask_cors import CORS, cross_origin
from datetime import datetime, timedelta, timezone
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity, \
                               unset_jwt_cookies, jwt_required, JWTManager
from models import db, Employees, Customers, Generators, ServiceRecords, Service_Employee_Int, Password_Recovery, Tasks, Projects
import csv, secrets, string, random, os
from datetime import datetime



api = Flask(__name__)
# Configure CORS
CORS(api,
     origins=[
         "http://localhost:5173",
         "https://bespokeprojectmanagerapp.vercel.app"
     ],
     allow_credentials=True,
     supports_credentials=True,
     expose_headers=["Content-Type", "X-CSRFToken"],
     allow_headers=["Content-Type", "Authorization"])

api.config['CORS_HEADERS'] = 'Content-Type'
api.config.from_object(ApplicationConfig)
bcrypt = Bcrypt(api)
db.init_app(api)

with api.app_context():
    db.create_all()
    file_path = 'testFile.csv'  # Optional seed file; skip if missing
    if os.path.exists(file_path):
        try:
            file = open(file_path)
            reader = csv.reader(file)
            header = next(reader)  # Pulls the first row of the csv file

            for row in reader:
                if Generators.query.filter_by(Generatorid=row[1]).first() is None:
                    new_generator = Generators(Generatorid=row[1], Name=row[0], Cost=row[2], Notes=row[3])
                    db.session.add(new_generator)
                    db.session.commit()
        finally:
            try:
                file.close()
            except Exception:
                pass

api.config["JWT_SECRET_KEY"] = "aosdflnasldfnaslndflnsdnlnlknlkgtudsrtstr"
jwt = JWTManager(api)

# we might not need this code anymore
# api.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
# @api.after_request
# def refresh_expiring_jwts(response):
#     try:
#         exp_timestamp = get_jwt()["exp"]
#         now = datetime.now(timezone.utc)
#         target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
#         if target_timestamp > exp_timestamp:
#             access_token = create_access_token(identity=get_jwt_identity())
#             data = response.get_json()
#             if type(data) is dict:
#                 data["access_token"] = access_token 
#                 response.data = json.dumps(data)
#         return response
#     except (RuntimeError, KeyError):
#         # Case where there is not a valid JWT. Just return the original response
#         return response


#The login route
@api.route('/token', methods=["POST"])
def create_token():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    remember = request.json.get("remember", None)

    forgot = request.json.get("forgot", None)

    user = Employees.query.filter_by(Email=email).first()
    user = Employees.query.filter_by(Email=email).first()
    access_token = create_access_token(identity=email)
    if user is None:
        return {"msg": "User Not Found"}, 401
    
    if not bcrypt.check_password_hash(user.Password, password):
        return {"msg": "Invalid Password"}, 401

    if remember:
        expires_delta = timedelta(days=7)
    else:
        expires_delta = timedelta(minutes=30)

    access_token = create_access_token(identity=email,expires_delta=expires_delta)
    response = {"access_token":access_token}

    return response


#The log out route
@api.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "Logout Successful"})
    unset_jwt_cookies(response)
    return response


# this function should return an array of employee objects with: 
# firstName, lastName, employeeID, and their username and password
@api.route('/employees', methods=["GET"])
@jwt_required()
def team():
    requester = Employees.query.filter_by(Email=get_jwt_identity()).first()
    team_list = []
    for i in Employees.query.all():
        # Only admins can see a recovery code; generate one if missing
        code_to_show = None
        if requester and requester.Admin:
            rec = Password_Recovery.query.filter_by(Email=i.Email).first()
            if rec is None:
                gen_code = ("".join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=10)))
                rec = Password_Recovery(Code=gen_code, Email=i.Email, Password=i.Password, DateMade=datetime.now().strftime("%Y-%m-%d"))
                db.session.add(rec)
                db.session.commit()
            code_to_show = rec.Code

        employee = {
            "fN": i.FirstName,
            "lN": i.LastName,
            "id": i.Employeeid,
            "admin": i.Admin,
            "email": i.Email,
            "phone": i.PhoneNumber,
            "hiredDate": i.DateHired,
            "role": i.Role,  # Added Role field
            "password": code_to_show,
        }
        team_list.append(employee)
    return team_list
    
#Password Recovery Route, creates a new code for the user
@api.route("/recovery/create", methods=["POST"])
def create_code():
    eid1 = request.json["EmployeeID"]
    datemade = request.json["creationDate"]

    user = Employees.query.filter_by(Employeeid = eid1).first()
    for i in Password_Recovery.query.filter_by(Email = user.Email).all():
        db.session.delete(i)

    code = ("".join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=10)))
    new_recovery = Password_Recovery(Code = code, Email = user.Email, Password = user.Password, DateMade = datemade)
    db.session.add(new_recovery)
    
    db.session.commit()
    return {"Code": new_recovery.Code}

#Password Recovery Route, checks that the code is correct and displays your password
@api.route("/recovery/check", methods=["POST"])
def check_code():
    email = request.json["email"]
    code = request.json["code"]
    new_password = request.json["new_password"]

    recovery = Password_Recovery.query.filter_by(Email = email).first()
    if recovery.Code == code:
        emp = Employees.query.filter_by(Email = email).first()
        emp.Password = bcrypt.generate_password_hash(new_password).decode("utf-8")
        db.session.delete(recovery)
        db.session.commit()
        return {"msg": "New Password Created"}
    else:
        return {"msg": "Invalid Code"}, 401

@api.route("/recovery/display", methods=["POST"])
@jwt_required()
def see_code():
    eid1 = request.json["EmployeeID"]
    emp = Employees.query.filter_by(Employeeid = eid1).first()
    recovery = Password_Recovery.query.filter_by(Email = emp.Email).first()
    
    return {"Code": recovery.Code}


#returns the currently logged in user's firstname and permission level
@api.route("/profile", methods=["GET"])
@jwt_required()
def my_profile():
    user = Employees.query.filter_by(Email=get_jwt_identity()).first()
    response_body = {
        "firstName": user.FirstName,
        "Admin": user.Admin,
        "ID": user.Employeeid,
        "Role": user.Role
    }

    return response_body

#Creating employees route
@api.route("/employees/create", methods=["POST"])
@cross_origin()
@jwt_required()
def create_employee():
    id1 = request.json["EmployeeID"]
    email1 = request.json["Email"]
    password1 = request.json["Password"]
    firstname1 = request.json["First Name"]
    lastname1 = request.json["Last Name"]
    phonenumber1 = request.json["Phone Number"]
    admin1 = request.json.get("Admin", False)  # Default to False if not provided
    # Support for Role: allow admin to create employees with specific roles (e.g., 'developer')
    role1 = request.json.get("Role", "employee")  # Default to 'employee' if not provided
    dateHired = request.json.get("hiredDate", datetime.now().strftime("%Y-%m-%d"))  # Default to current date

    employee_exists = Employees.query.filter_by(Employeeid = id1).first() is not None

    if employee_exists:
        abort(409)

    hashed_password = bcrypt.generate_password_hash(password1).decode("utf-8")
    new_employee = Employees(Employeeid = id1, Email = email1, Password = hashed_password, FirstName = firstname1, LastName = lastname1, PhoneNumber = phonenumber1, Admin = admin1, Role = role1, DateHired = dateHired)
    db.session.add(new_employee)
    db.session.commit()

    return jsonify({
        "ID": new_employee.Employeeid,
        "Email": new_employee.Email,
        "First Name": new_employee.FirstName,
        "Last Name": new_employee.LastName
        })


#Deleting employees route
@api.route("/employees/delete", methods=["POST"])
@cross_origin()
@jwt_required()
def delete_employee():
    # only an admin can delete employees
    user = Employees.query.filter_by(Email=get_jwt_identity()).first()
    if user.Admin == True:
        reqs = request.get_json()
        id1 = reqs.get("EmployeeID")

        employee_exists = Employees.query.filter_by(Employeeid = id1).first() is not None

        if not employee_exists:
            abort(409)
            
        Employees.query.filter_by(Employeeid = id1).delete()
        db.session.commit()
        
        return jsonify({"ID": id1})


#Changes user between admin/user
@api.route("/employees/permission", methods=["POST"])
@cross_origin()
@jwt_required()
def change_permission():
    empID = request.json.get("EmployeeID", None)

    user = Employees.query.filter_by(Employeeid = empID).first()

    if user is None:
        abort(409)
        
    user.Admin = not user.Admin
    db.session.commit()
    
    return jsonify({"Permission changed for ID": empID})
    

#Search and Display Customers    
@api.route("/customer/display", methods=["POST"])
@cross_origin()
@jwt_required()
def display_customers():

    reqs = request.get_json()
    searchTerm = reqs.get("Search")
    customer_list = []
    user = Employees.query.filter_by(Email=get_jwt_identity()).first()
    for i in Customers.query.filter(or_(Customers.FirstName.like('%' + searchTerm + '%'),
                                        Customers.LastName.like('%' + searchTerm + '%'))):
        customer = {
            "ID": i.Customerid,
            "FirstName": i.FirstName,
            "LastName": i.LastName,
            "Email": i.Email,
            "Phone": i.PhoneNumber,
            "City": i.City,
            "Street": i.Street,
            "State": i.State,
            "ZIP": i.ZIP
        }
        customer_list.append(customer)
    return jsonify({"customers":customer_list, "admin": user.Admin})


#Shows all of a single customer's details
@api.route("/customer/details", methods=["POST"])
@cross_origin()
@jwt_required()
def customer_details():
    reqs = request.get_json()
    id1 = reqs.get("clientID")
    user = Employees.query.filter_by(Email=get_jwt_identity()).first()
    i = Customers.query.filter_by(Customerid = id1).first()

    customer = {
            "ID": i.Customerid,
            "FirstName": i.FirstName,
            "LastName": i.LastName,
            "Email": i.Email,
            "Phone": i.PhoneNumber,
            "City": i.City,
            "Street": i.Street,
            "State": i.State,
            "ZIP": i.ZIP
        }

    return jsonify({"details":customer, "admin": user.Admin})



#Creating Customers
@api.route('/customer/create', methods=["POST"])
@cross_origin()
@jwt_required()
def create_customer():
    id1 = request.json["CustomerID"]
    firstname1 = request.json["First Name"]
    lastname1 = request.json["Last Name"]
    email1 = request.json["Email"]
    city1 = request.json["City"]
    street1 = request.json["Street"]
    phonenumber1 = request.json["Phone Number"]
    state1 = request.json["State"]
    Zip1 = request.json["ZIP Code"]
    
    customer_exists = Customers.query.filter_by(Customerid = id1).first() is not None

    if customer_exists:
        abort(409)

    new_customer = Customers(Customerid = id1, FirstName = firstname1, LastName = lastname1, Email = email1, City = city1, Street = street1, PhoneNumber = phonenumber1, State = state1, ZIP = Zip1)
    db.session.add(new_customer)
    db.session.commit()

    return jsonify({
        "ID": new_customer.Customerid,
        "First Name": new_customer.FirstName,
        "Last Name": new_customer.LastName,
        "Email": new_customer.Email,
        "City": new_customer.City,
        "Street": new_customer.Street,
        "State": new_customer.State,
        "ZIP": new_customer.ZIP,
        "Phone Number": new_customer.PhoneNumber
        })

#Deleting Customers
@api.route("/customer/delete", methods=["POST"])
@cross_origin()
@jwt_required()
def delete_customer():
    reqs = request.get_json()
    id1 = reqs.get("CustomerID")

    customer_exists = Customers.query.filter_by(Customerid = id1).first() is not None

    if not customer_exists:
        abort(409)

    Customers.query.filter_by(Customerid = id1).delete()
    db.session.commit()

    return jsonify({"ID": id1})


#Creates a new service record in the database, checks for errors while creating
@api.route("/service/create", methods=["POST"])
@jwt_required()
def create_service():
    id1 = request.json["ServiceID"]
    customerid1 = request.json["CustomerID"]
    generatorid1 = request.json["GeneratorID"]
    performed1 = request.json["ServicePerformed"]
    startdate1 = request.json["Date"]
    starttime1 = request.json["Time"]
    reqs = request.get_json()
    servicetype1 = reqs.get("ServiceType")
    notes1 = request.json["Notes"]
    
    service_exists = ServiceRecords.query.filter_by(Serviceid = id1).first() is not None

    if service_exists:
        abort(409)

    new_service = ServiceRecords(Serviceid = id1, Customerid = customerid1, Generatorid = generatorid1, ServicePerformed = performed1, ServiceType = servicetype1, StartDate = startdate1, StartTime = starttime1, Notes = notes1)
    
    db.session.add(new_service)
    db.session.commit()

    return jsonify({
        "ID": new_service.Serviceid,
        "Customer Name": new_service.Customerid,
        "Generator Type": new_service.Generatorid,
        "Service Performed": new_service.ServicePerformed,
        "Start Date": new_service.StartDate,
        "Start Time": new_service.StartTime,
        "Notes": new_service.Notes
        })

@api.route("/generators/details", methods=["GET"])
@jwt_required()
def retrieve_generators():
    gList = []
    for g in Generators.query.all():
        generator =  {
            "gID" : g.Generatorid,
            "gName" : g.Name,
            "gCost" : g.Cost,
            "gNotes" : g.Notes
        }
        gList.append(generator)

    return gList

@api.route("/service/details", methods=["POST"])
@jwt_required()
def retrieve_services():
    reqs = request.get_json()
    id1 = reqs.get("CustomerID")
    services = []

    if id1 is None:
        # If no CustomerID provided, return all service records for all customers
        for i in ServiceRecords.query.all():
            gName = Generators.query.filter_by(Generatorid = i.Generatorid).first()
            services.append({
                "CustomerID": i.Customerid,
                "Generator": gName.Name,
                "ServiceType": i.ServiceType,
                "Date": i.StartDate,
                "Time": i.StartTime,
                "Notes": i.Notes,
            })
    else:
        # If a CustomerID is provided, return service records for that customer
        service_exists = ServiceRecords.query.filter_by(Customerid = id1).first() is not None

        if not service_exists:
            abort(409)

        for i in ServiceRecords.query.filter_by(Customerid = id1).all():
            gName = Generators.query.filter_by(Generatorid = i.Generatorid).first()
            services.append({
                "Generator": gName.Name,
                "ServiceType": i.ServiceType,
                "Date": i.StartDate,
                "Time": i.StartTime,
                "Notes": i.Notes,
            })

    return services




#edit jobs from schedule page
#Doable by admin accounts
@api.route("/schedule/edit", methods=["POST"])
@jwt_required()
def edit_Job():
    #Checking that user is Admin
    user = Employees.query.filter_by(Email=get_jwt_identity()).first()
    reqs = request.get_json()
    sid = reqs.get("ServiceID")
    generatorname = reqs.get("GeneratorName")
    startdate = reqs.get("Date")
    starttime = reqs.get("Time")
    servicetype = reqs.get("ServiceType")
    notes = reqs.get("Notes")

    if user.Admin == True:
        service = ServiceRecords.query.filter_by(Serviceid = sid).first()
        service.Generatorid = generatorname
        service.StartDate = startdate
        service.StartTime = starttime
        service.ServiceType = servicetype
        service.Notes = notes
        
        db.session.commit()
        
        return jsonify({
        "service_id": sid,
        "generator_name": generatorname,
        "start_date": startdate,
        "start_time": starttime,
        "service_type": servicetype,
        "notes": notes,
    })

    return
    
#Adds technicians to jobs
#Doable by admins
@api.route("/schedule/techs", methods = ["POST"])
@jwt_required()
def add_techs():  
    
    #Checking that user is Admin
    user = Employees.query.filter_by(Email=get_jwt_identity()).first()

    if user.Admin == True:
        reqs = request.get_json()
        sid = reqs.get("ServiceID")
        tech_id = []
        tech_id.append(request.json["FirstEmployeeID"])
        tech_id.append(request.json["SecondEmployeeID"])
        tech_id.append(request.json["ThirdEmployeeID"])
        tech_id.append(request.json["FourthEmployeeID"])

        for i in Service_Employee_Int.query.filter_by(Serviceid = sid).all():
            db.session.delete(i)
            db.session.commit()

        for k in tech_id:
            if k != "default":
                assigned = Service_Employee_Int(Serviceid = sid, Employeeid = k)
                db.session.add(assigned)
        
        db.session.commit()

        return jsonify({
            "ServiceID": sid,
            "First_Employee_ID": tech_id[0],
            "Second_Employee_ID": tech_id[1],
            "Third_Employee_ID": tech_id[2],
            "Fourth_Employee_ID": tech_id[3],
        })

# Completes a job from the schedule page and sets the finish date/time 
# Doable by everyone who this shows up for
@api.route("/schedule/complete", methods = ["POST"])
@jwt_required()
def complete_job():
    reqs = request.get_json()
    sid = reqs.get("ServiceID")
    finishdate = reqs.get("completeDate")
    finishtime = reqs.get("completeTime")
    service = ServiceRecords.query.filter_by(Serviceid = sid).first()
    
    if service.ServicePerformed == False:
        service.ServicePerformed = True
        service.FinishDate = finishdate
        service.FinishTime = finishtime
    else:
        service.ServicePerformed = False
        service.FinishDate = None
        service.FinishTime = None
    
    
 
    db.session.commit()

    return jsonify({
        "ServiceID": service.Serviceid,
        "Service_Performed": service.ServicePerformed,
        "Finish Date": service.FinishDate,
        "Finish Time": service.FinishTime
    })

#Displays Upcoming Services
@api.route("/schedule/display", methods = ["POST"])
@jwt_required()
def get_all_services():
    start_date = request.json.get("startDate", None)
    end_date = request.json.get("endDate", None)
    services = []
    techs = []
    user = Employees.query.filter_by(Email=get_jwt_identity()).first()
    if start_date is None and end_date is None:
        service_records = ServiceRecords.query.all()
    else:
        service_records = ServiceRecords.query.filter(ServiceRecords.StartDate.between(start_date, end_date)).all()
    
    #This Code May No Longer Be Necessary
    #if not service_records:
       # return jsonify({'message': 'no jobs found'})

    for service in service_records:
        customer = Customers.query.filter_by(Customerid=service.Customerid).first()
        generator = Generators.query.filter_by(Generatorid=service.Generatorid).first()

        if user.Admin == True:
            for ser_emp_int in Service_Employee_Int.query.filter_by(Serviceid = service.Serviceid).all():
                emp = Employees.query.filter_by(Employeeid = ser_emp_int.Employeeid).first()
                techs.append({
                    'service_id': service.Serviceid,
                    'employee_first_name': emp.FirstName,
                    'employee_last_name': emp.LastName
                })

            services.append({
                'service_id': service.Serviceid,
                'customer_first_name': customer.FirstName,
                'customer_last_name': customer.LastName,
                'city': customer.City,
                'street': customer.Street,
                'generator_name': generator.Name,
                'service_type': service.ServiceType,
                'start_date': service.StartDate,
                'start_time': service.StartTime,
                'finish_date': service.FinishDate,
                'finish_time': service.FinishTime,
                'notes': service.Notes
            })

        else:
            for guy in Service_Employee_Int.query.filter_by(Employeeid = user.Employeeid).all():
                if service.Serviceid == guy.Serviceid:
                    techs.append({
                        'service_id': service.Serviceid,
                        'employee_first_name': user.FirstName,
                        'employee_last_name': user.LastName
                    })

                    services.append({
                        'service_id': service.Serviceid,
                        'customer_first_name': customer.FirstName,
                        'customer_last_name': customer.LastName,
                        'city': customer.City,
                        'street': customer.Street,
                        'generator_name': generator.Name,
                        'service_type': service.ServiceType,
                        'start_date': service.StartDate,
                        'start_time': service.StartTime,
                        'finish_date': service.FinishDate,
                        'finish_time': service.FinishTime,
                        'notes': service.Notes
                    })

    return jsonify({'services': services, 'techs': techs, 'team': team(), 'admin': user.Admin, 'generators': retrieve_generators()})

#Deletes Jobs from the schedule page
#Doable by Admins
@api.route("/schedule/delete", methods = ["POST"])
@jwt_required()
def delete_job():
    
    #Checking if logged in user is an admin
    user = Employees.query.filter_by(Email=get_jwt_identity()).first()

    if user.Admin == True:
        reqs = request.get_json()
        id1 = reqs.get("ServiceID")

        service_exists = ServiceRecords.query.filter_by(Serviceid = id1).first() is not None

        if not service_exists:
            abort(409)

        badrecord = ServiceRecords.query.filter_by(Serviceid = id1).first()
        #Deletes ser_emp_int records that go with the service record being deleted
        for i in Service_Employee_Int.query.filter_by(Serviceid = id1).all():
            db.session.delete(i)
        db.session.delete(badrecord)
        db.session.commit()

    return jsonify({"ID": id1})

# Project Management Routes
@api.route("/projects/create", methods=["POST"])
@jwt_required()
def create_project():
    # Only project managers and admins can create projects
    user = Employees.query.filter_by(Email=get_jwt_identity()).first()
    if not (user.Admin or user.Role == "project_manager"):
        return {"msg": "Unauthorized"}, 401

    name = request.json["Name"]
    description = request.json.get("Description")  # Optional
    customerid = request.json["CustomerID"]
    start_date = request.json["StartDate"]
    due_date = request.json["DueDate"]
    status = request.json.get("Status", "pending")

    # Generate project ID
    max_id = db.session.query(db.func.max(Projects.Projectid)).scalar() or 0
    new_id = max_id + 1

    new_project = Projects(
        Projectid=new_id,
        Name=name,
        Description=description,
        Status=status,
        StartDate=start_date,
        DueDate=due_date,
        Customerid=customerid,
        Managerid=user.Employeeid,
        CreatedDate=datetime.now().strftime("%Y-%m-%d"),
        UpdatedDate=datetime.now().strftime("%Y-%m-%d")
    )
    db.session.add(new_project)
    db.session.commit()

    return jsonify({
        "ID": new_project.Projectid,
        "Name": new_project.Name,
        "Status": new_project.Status,
        "StartDate": new_project.StartDate,
        "DueDate": new_project.DueDate
    })

@api.route("/projects/list", methods=["GET"])
@jwt_required()
def list_projects():
    user = Employees.query.filter_by(Email=get_jwt_identity()).first()
    
    # If user is admin or project manager, show all projects
    if user.Admin or user.Role == "project_manager":
        projects_query = Projects.query
    else:
        # For regular users (clients), only show their projects
        projects_query = Projects.query.join(Customers).filter(Customers.Email == user.Email)
    
    projects = []
    for project in projects_query.all():
        customer = Customers.query.get(project.Customerid)
        manager = Employees.query.get(project.Managerid)
        
        projects.append({
            "id": project.Projectid,
            "name": project.Name,
            "description": project.Description,
            "status": project.Status,
            "startDate": project.StartDate,
            "dueDate": project.DueDate,
            "customer": {
                "id": customer.Customerid,
                "name": f"{customer.FirstName} {customer.LastName}"
            },
            "manager": {
                "id": manager.Employeeid,
                "name": f"{manager.FirstName} {manager.LastName}"
            },
            "createdDate": project.CreatedDate,
            "updatedDate": project.UpdatedDate
        })
    
    return jsonify({"projects": projects})

@api.route("/projects/update", methods=["POST"])
@jwt_required()
def update_project():
    user = Employees.query.filter_by(Email=get_jwt_identity()).first()
    if not (user.Admin or user.Role == "project_manager"):
        return {"msg": "Unauthorized"}, 401

    projectid = request.json["ProjectID"]
    project = Projects.query.get(projectid)
    
    if not project:
        return {"msg": "Project not found"}, 404
        
    # Update allowed fields
    if "Name" in request.json:
        project.Name = request.json["Name"]
    if "Description" in request.json:
        project.Description = request.json["Description"]
    if "Status" in request.json:
        project.Status = request.json["Status"]
    if "StartDate" in request.json:
        project.StartDate = request.json["StartDate"]
    if "DueDate" in request.json:
        project.DueDate = request.json["DueDate"]
    if "CustomerID" in request.json and user.Admin:  # Only admins can reassign customers
        project.Customerid = request.json["CustomerID"]
    if "ManagerID" in request.json and user.Admin:  # Only admins can reassign managers
        project.Managerid = request.json["ManagerID"]
    
    project.UpdatedDate = datetime.now().strftime("%Y-%m-%d")
    db.session.commit()
    
    return jsonify({
        "ID": project.Projectid,
        "Name": project.Name,
        "Status": project.Status,
        "UpdatedDate": project.UpdatedDate
    })

@api.route("/projects/delete", methods=["POST"])
@jwt_required()
def delete_project():
    user = Employees.query.filter_by(Email=get_jwt_identity()).first()
    if not (user.Admin or user.Role == "project_manager"):
        return {"msg": "Unauthorized"}, 401

    projectid = request.json["ProjectID"]
    project = Projects.query.get(projectid)
    
    if not project:
        return {"msg": "Project not found"}, 404
        
    db.session.delete(project)
    db.session.commit()
    
    return jsonify({"ID": projectid})

# Task Management Routes
@api.route("/tasks/create", methods=["POST"])
@jwt_required()
def create_task():
    user = Employees.query.filter_by(Email=get_jwt_identity()).first()
    if not (user.Admin or user.Role == "project_manager"):
        return {"msg": "Unauthorized"}, 401

    title = request.json.get("Title", "Untitled Task")  # Made optional with default
    description = request.json.get("Description")
    projectid = request.json.get("ProjectID")  # Made optional
    assigned_to = request.json.get("AssignedTo")
    due_date = request.json.get("DueDate")
    priority = request.json.get("Priority", "medium")
    status = request.json.get("Status", "pending")

    # Generate task ID
    max_id = db.session.query(db.func.max(Tasks.Taskid)).scalar() or 0
    new_id = max_id + 1

    # Verify project if specified
    if projectid:
        project = Projects.query.get(projectid)
        if not project:
            return {"msg": "Project not found"}, 404

    # Verify developer if assigned
    if assigned_to:
        developer = Employees.query.get(assigned_to)
        if not developer:
            return {"msg": "Developer not found"}, 404
        if developer.Role != "developer":
            return {"msg": "Tasks can only be assigned to developers"}, 400

    new_task = Tasks(
        Taskid=new_id,
        Title=title,
        Description=description,
        Status=status,
        Priority=priority,
        DueDate=due_date,
        Projectid=projectid,
        AssignedTo=assigned_to,
        CreatedBy=user.Employeeid,
        CreatedDate=datetime.now().strftime("%Y-%m-%d"),
        UpdatedDate=datetime.now().strftime("%Y-%m-%d")
    )
    db.session.add(new_task)
    db.session.commit()

    return jsonify({
        "ID": new_task.Taskid,
        "Title": new_task.Title,
        "Status": new_task.Status,
        "Priority": new_task.Priority,
        "DueDate": new_task.DueDate
    })

@api.route("/tasks/list", methods=["GET"])
@jwt_required()
def list_tasks():
    user = Employees.query.filter_by(Email=get_jwt_identity()).first()
    
    # Project managers see all tasks they created
    # Developers see tasks assigned to them
    # Admins see all tasks
    if user.Admin:
        tasks_query = Tasks.query
    elif user.Role == "project_manager":
        tasks_query = Tasks.query.filter_by(CreatedBy=user.Employeeid)
    else:  # developer
        tasks_query = Tasks.query.filter_by(AssignedTo=user.Employeeid)
    
    tasks = []
    for task in tasks_query.all():
        project = Projects.query.get(task.Projectid)
        developer = Employees.query.get(task.AssignedTo)
        manager = Employees.query.get(task.CreatedBy)
        
        tasks.append({
            "id": task.Taskid,
            "title": task.Title,
            "description": task.Description,
            "status": task.Status,
            "priority": task.Priority,
            "dueDate": task.DueDate,
            "project": {
                "id": project.Projectid,
                "name": project.Name
            },
            "assignedTo": {
                "id": developer.Employeeid,
                "name": f"{developer.FirstName} {developer.LastName}"
            },
            "createdBy": {
                "id": manager.Employeeid,
                "name": f"{manager.FirstName} {manager.LastName}"
            },
            "createdDate": task.CreatedDate,
            "updatedDate": task.UpdatedDate
        })
    
    return jsonify({"tasks": tasks})

@api.route("/tasks/update", methods=["POST"])
@jwt_required()
def update_task():
    user = Employees.query.filter_by(Email=get_jwt_identity()).first()
    taskid = request.json["TaskID"]
    task = Tasks.query.get(taskid)
    
    if not task:
        return {"msg": "Task not found"}, 404
        
    # Only creator (project manager) or admin can update task details
    # Developer can only update status
    is_manager = task.CreatedBy == user.Employeeid
    is_developer = task.AssignedTo == user.Employeeid
    
    if not (user.Admin or is_manager or is_developer):
        return {"msg": "Unauthorized"}, 401

    # Developers can only update status
    if is_developer and not user.Admin and not is_manager:
        if "Status" not in request.json:
            return {"msg": "Developers can only update task status"}, 400
        task.Status = request.json["Status"]
    else:
        # Admin/Project Manager updates
        if "Title" in request.json:
            task.Title = request.json["Title"]
        if "Description" in request.json:
            task.Description = request.json["Description"]
        if "Status" in request.json:
            task.Status = request.json["Status"]
        if "Priority" in request.json:
            task.Priority = request.json["Priority"]
        if "DueDate" in request.json:
            task.DueDate = request.json["DueDate"]
        if "AssignedTo" in request.json:
            new_developer = Employees.query.get(request.json["AssignedTo"])
            if not new_developer or new_developer.Role != "developer":
                return {"msg": "Invalid developer assignment"}, 400
            task.AssignedTo = request.json["AssignedTo"]
    
    task.UpdatedDate = datetime.now().strftime("%Y-%m-%d")
    db.session.commit()
    
    return jsonify({
        "ID": task.Taskid,
        "Title": task.Title,
        "Status": task.Status,
        "UpdatedDate": task.UpdatedDate
    })

@api.route("/tasks/delete", methods=["POST"])
@jwt_required()
def delete_task():
    user = Employees.query.filter_by(Email=get_jwt_identity()).first()
    if not (user.Admin or user.Role == "project_manager"):
        return {"msg": "Unauthorized"}, 401

    taskid = request.json["TaskID"]
    task = Tasks.query.get(taskid)
    
    if not task:
        return {"msg": "Task not found"}, 404
    
    # Only creator or admin can delete tasks
    if not user.Admin and task.CreatedBy != user.Employeeid:
        return {"msg": "Unauthorized"}, 401
        
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({"ID": taskid})


if __name__ == "__main__":
    # Allow running the backend directly on port 3000 for development on Windows
    # This matches the frontend axios calls that target http://127.0.0.1:3000
    api.run(host="127.0.0.1", port=3000)