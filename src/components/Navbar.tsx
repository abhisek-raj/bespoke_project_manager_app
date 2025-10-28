import { useEffect, useState } from "react";
import { BiLogOut, BiMenu } from "react-icons/bi";
import { CgChevronRight } from "react-icons/cg";
import axios from "axios";
import { useLocation } from "react-router-dom";
import { config } from "../config";

const Navbar = (props: any) => {
  const [name, setName] = useState<string>("");
  const [role, setRole] = useState<string>("client");
  const [isAdmin, setIsAdmin] = useState<boolean>(false);
  const [nav, setNav] = useState<Boolean>(false);
  const location = useLocation();

  function getData() {
    axios({
      method: "GET",
      url: `${config.apiUrl}/profile`,
      headers: {
        Authorization: "Bearer " + props.token,
      },
    })
      .then((response) => {
        const res = response.data;
        res.access_token && props.setToken(res.access_token);
  setName(res.firstName || "");
  // Respect Admin flag first (preserve old admin behavior), otherwise use Role
  const adminFlag = !!res.Admin;
  setIsAdmin(adminFlag);
  setRole(adminFlag ? "admin" : (res.Role ?? "client"));
      })
      .catch((error) => {
        console.log(error);
        props.removeToken();
        // removes the users token if it's no longer valid
      });
  }
  function logOut() {
    axios({
      method: "POST",
      url: `${config.apiUrl}/logout`,
    })
      .then((response) => {
        console.log(response.data);
        props.removeToken();
      })
      .catch((error) => {
        if (error.response) {
          console.log(error.response);
          console.log(error.response.status);
          console.log(error.response.headers);
        }
      });
  }
  const getNavLinks = () => [
    {
      title: "Home",
      path: "/",
      roles: ["admin", "project_manager", "client"],
    },
    {
      title: "Team",
      path: "/team",
      roles: ["admin"],
    },
    {
      title: "Clients",
      path: "/clients",
      roles: ["admin", "project_manager"],
    },
    {
      title: "Projects",
      path: "/projects",
      roles: ["admin", "project_manager", "client"],
    },
    {
      title: "Schedule",
      path: "/schedule",
      roles: ["admin", "project_manager", "client"],
    },
  ];
  useEffect(() => {
    getData();
  }, []);
  return (
    <>
      <div className="h-[50px] w-full bg-slate-700 select-none text-white border-b-2 border-slate-500 flex justify-between tracking-wide shadow-lg shadow-slate-600">
        <div className="my-auto px-4 flex">
          <p>Hello 👋, {name}</p>
          <p className="ml-2 mt-2 text-gray-400 text-[10px]">
            {(role || "client").toUpperCase()}
          </p>
        </div>
        <div className="px-2 my-auto">
          <ul className="hidden md:flex">
            {getNavLinks().map((item, index) => {
              const userRole = isAdmin ? "admin" : role;
              return item.roles.includes(userRole) ? (
                <a 
                  href={item.path} 
                  key={index} 
                  className={`px-4 border-b-2 ${
                    location.pathname === item.path
                      ? "border-blue-500"
                      : "border-transparent hover:border-blue-500"
                  } ease-in-out duration-300 transition-all`}
                >
                  {item.title}
                </a>
              ) : null
            })}
            <button className="text-gray-200 mr-2" onClick={logOut}>
              <BiLogOut size={22} />
            </button>
          </ul>
          <div className="flex md:hidden cursor-pointer">
            <BiMenu size={30} onClick={() => setNav(true)} />
          </div>
        </div>
      </div>
      {/* mobile nav menu */}
      <div
        className={
          nav
            ? "h-screen select-none w-full fixed md:hidden top-0 left-0 bg-black/70 opacity-100 transition-all duration-300 ease-in"
            : "h-screen select-none w-0 fixed md:hidden top-0 left-0 bg-black/70 opacity-0 transition-all duration-300 ease-out"
        }
        onClick={() => setNav(false)}
      >
        {nav ? (
          <>
            <div className="bg-slate-700 border-2 border-slate-500 w-[50%] p-4 h-screen">
              <div className="select-none">
                <h1
                  className={`font-pacifico text-center tracking-wide text-white text-[25px]`}
                >
                  BESPOKE TECH FAMILY
                </h1>
                <h2
                  className={`font-roboto text-center text-gray-400 text-[15}px] tracking-widest`}
                >
                  {(role || "client").toUpperCase()}
                </h2>
              </div>
              <div className="ml-4">
                <ul className="mt-8">
                    {getNavLinks().map((item, index) => {
                      const userRole = isAdmin ? "admin" : role;
                      return item.roles.includes(userRole) ? (
                      <a href={item.path} key={index}>
                          <li className={`text-white py-6 flex justify-between tracking-wider ${
                            location.pathname === item.path ? "text-blue-500" : ""
                          }`}>
                          {item.title}
                          <CgChevronRight size={20} className={"mr-2"} />
                        </li>
                        <div className="bg-slate-700/70 w-full h-0.5 rounded-lg" />
                      </a>
                    ) : null
                    })}
                </ul>
              </div>
              <button
                className="bg-blue-500 border-2 border-blue-800 text-lg px-4 py-2 rounded-lg w-full hover:bg-blue-700 transition-all ease-in-out duration-300"
                onClick={props.removeToken}
              >
                Sign Out
              </button>
            </div>
          </>
        ) : null}
      </div>
    </>
  );
};

export default Navbar;
