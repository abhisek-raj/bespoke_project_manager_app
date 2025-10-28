import axios from "axios";
import { useEffect, useState } from "react";
import toast, { Toaster } from "react-hot-toast";
import Employee from "../components/Employee";
import Footer from "../components/Footer";

const Team = (props: any) => {
  const API = import.meta.env.VITE_API_URL as string;
  const [menu, setMenu] = useState<boolean>(false);
  const [first, setFirst] = useState<string>("");
  const [last, setLast] = useState<string>("");
  const [num, setNum] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [role, setRole] = useState<string>("employee");
  const [teamMembers, setTeamMembers] = useState<any>([]);
  const [userID, setUserID] = useState<number | undefined>();
  const [access, setAccess] = useState<boolean | undefined>();
  const time = new Date();

  // Gets the profile of team members as well as their information
  function getProfile() {
    axios({
      method: "GET",
      url: `${API}/profile`,
      headers: {
        Authorization: "Bearer " + props.token,
      },
    })
      .then((response) => {
        const res = response.data;
        res.access_token && props.setToken(res.access_token);
        // only load data if admin is logged in
        if (res.Admin == true) {
          setAccess(res.Admin);
          setUserID(res.ID);
          getTeam();
        }
      })
      .catch((error) => {
        console.log(error);
      });
  }
  {
    // Shows the team member page
  }
  function getTeam() {
    axios({
      method: "GET",
      url: `${API}/employees`,
      headers: {
        Authorization: "Bearer " + props.token,
      },
    })
      .then((response) => {
        const employees = response.data;
        setTeamMembers(employees);
      })
      .catch((error) => {
        if (error.response) {
          console.log(error.response);
        }
      });
  }

  // Creates new employee and assigns a random employee ID number
  function addEmployee(e: any) {
    e.preventDefault();
    axios({
      method: "POST",
      url: `${API}/employees/create`,
      headers: {
        Authorization: "Bearer " + props.token,
      },
      data: {
        EmployeeID: Math.floor(Math.random() * 90000) + 10000,
        Email: email,
        Password: password,
        "First Name": first.charAt(0).toUpperCase() + first.slice(1),
        "Last Name": last.charAt(0).toUpperCase() + last.slice(1),
        "Phone Number": num,
        Admin: false, // all new accounts start as non-admin
        Role: role,
        hiredDate:
          time.getMonth() + 1 + "/" + time.getDate() + "/" + time.getFullYear(),
      },
    })
      .then((response) => {
        toast.success("Employee Added");
        console.log(response);
        setFirst("");
        setLast("");
        setNum("");
        setEmail("");
        setPassword("");
        setMenu(false);
        getTeam();
      })
      .catch((error) => {
        toast.error("Something Went Wrong");
        if (error.response) {
          console.log(error.response);
        }
      });
  }

  useEffect(() => {
    getProfile();
  }, []);

  return (
    <>
      <Toaster />
      <div className="flex justify-center mt-5">
        {access ? (
          <div className="max-w-[550px] w-[90%]">
            <div className="grid grid-cols-1 gap-4 px-4">
              <div
                className={
                  menu
                    ? "bg-slate-700 border-2 border-slate-500 shadow-md shadow-slate-700 mb-2 rounded-xl h-[640px] transition-all duration-300 ease-in-out"
                    : "bg-slate-700 border-2 border-slate-500 shadow-md shadow-slate-700 mb-2 rounded-xl md:h-[150px] transition-all duration-300 ease-in-out"
                }
              >
                <div className="flex justify-center">
                  <div className="w-[500px] p-4">
                    <h2 className="text-white cap font-roboto text-center text-4xl tracking-wide">
                      Manage Employees
                    </h2>
                    <h3 className="text-gray-300 uppercase text-sm my-1 text-center tracking-wider">
                      {teamMembers.length} Total Employees
                    </h3>
                    <div className="flex justify-center">
                      {!menu ? (
                        <button
                          className="bg-blue-500 border-2 border-blue-800 text-lg px-4 py-2 rounded-lg w-full hover:bg-blue-700 transition-all ease-in-out duration-300"
                          onClick={() => setMenu(true)}
                        >
                          New Employee
                        </button>
                      ) : (
                        <button
                          className="bg-red-500 border-2 border-red-800 text-lg px-4 py-2 rounded-lg mt-2 w-full hover:bg-red-700 transition-all ease-in-out duration-300"
                          onClick={() => setMenu(false)}
                        >
                          Cancel
                        </button>
                      )}
                    </div>
                    <div
                      className={
                        menu
                          ? "opacity-1 transition-all ease-in-out duration-500"
                          : "opacity-0 transition-all ease-in-out duration-500"
                      }
                    >
                      {/* add new employee dropdown menu */}
                      {menu ? (
                        <>
                          <form onSubmit={addEmployee}>
                            <label>First name</label>
                            <input
                              type="text"
                              placeholder="John"
                              onChange={(e) => setFirst(e.target.value)}
                              value={first}
                              required
                            />
                            <label>Last name</label>
                            <input
                              type="text"
                              placeholder="Smith"
                              onChange={(e) => setLast(e.target.value)}
                              value={last}
                              required
                            />
                            <label>Phone number</label>
                            <input
                              type="text"
                              pattern="[1-9]{1}[0-9]{9}"
                              maxLength={10}
                              placeholder="1-234-6789"
                              onChange={(e) => setNum(e.target.value)}
                              value={num}
                              required
                            />
                            <label>Email:</label>
                            <input
                              type="email"
                              placeholder="Johnsmith@gmail.com"
                              onChange={(e) => setEmail(e.target.value)}
                              value={email}
                              required
                            />
                            <label>Password:</label>
                            <input
                              type="password"
                              placeholder="&#9679;&#9679;&#9679;&#9679;&#9679;&#9679;&#9679;&#9679;"
                              onChange={(e) => setPassword(e.target.value)}
                              value={password}
                              required
                            />
                            <label>Role:</label>
                            <select
                              value={role}
                              onChange={(e) => setRole(e.target.value)}
                              className="w-full mb-2"
                            >
                              <option value="employee">User</option>
                              <option value="project_manager">Project Manager</option>
                              <option value="developer">Developer</option>
                            </select>
                            <div className="flex justify-center">
                              <button
                                type="submit"
                                className="bg-blue-500 border-2 font-bold border-blue-800 text-lg px-4 py-2 rounded-lg my-4 w-full hover:bg-blue-700 transition-all ease-in-out duration-300"
                              >
                                Create User Profile
                              </button>
                            </div>
                          </form>
                        </>
                      ) : null}
                    </div>
                  </div>
                </div>
              </div>
              <div className="h-1 rounded-full bg-slate-500" />
              {/* list of employees */}
              {teamMembers.map((item: any) => (
                <Employee
                  item={item}
                  key={item.id}
                  userID={userID}
                  getTeam={getTeam}
                  token={props.token}
                />
              ))}
            </div>
          </div>
        ) : (
          <h2 className="text-white font-bold uppercase my-20 font-roboto text-center text-4xl tracking-wide">
            Access Denied
          </h2>
        )}
      </div>
      <Footer />
    </>
  );
};

export default Team;
