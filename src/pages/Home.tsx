import { useEffect, useState } from "react";
import { BsPersonFill, BsCalendarFill } from "react-icons/bs";
import { RiTeamFill } from "react-icons/ri";
import { BiLogOut } from "react-icons/bi";
import axios from "axios";
import Footer from "../components/Footer";
import { config } from "../config";

const Home = (props: any) => {
  const [name, setName] = useState<String>();
  const [admin, setAdmin] = useState<Boolean>();

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
        setName(res.firstName);
        setAdmin(Boolean(res.Admin));
      })
      .catch((error) => {
        if (error.response) {
          console.log(error.response);
          console.log(error.response.status);
          console.log(error.response.headers);
        }
      });
  }

  // logs out the user and removes their token
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

  useEffect(() => {
    getData();
  }, []);

  const iconSize: number = 60;
  const styles = {
    container:
      "bg-slate-700 text-white select-none draggable-none p-2 flex rounded-lg border-2 border-slate-500 shadow-lg shadow-slate-700 hover:bg-blue-600 hover:scale-105 duration-300 ease-in-out transition-all",
    text: "text-2xl mx-auto my-auto font-bold tracking-wide",
  };

  // Home page layout, references the different pages of the system
  return (
    <>
      <div className="flex justify-center md:mt-20">
        <div className="w-[600px]">
          <div className="text-gray-100 text-[40px] md:text-[50px] font-pacifico tracking-wider text-center mt-4 select-none">
            Welcome, {name}
          </div>
          <h2 className="font-roboto uppercase text-center mb-4 -mt-2 text-gray-600 font-bold text-xl tracking-wider select-none">
            {admin ? "Admin" : "User"}
          </h2>
          {admin ? (
            <div className="bg-blue-500/20 border-2 border-blue-500 rounded-lg p-4 mx-4 mb-4">
              <p className="text-gray-200 text-center text-sm md:text-base">
                👋 Hey Admin! You can create <span className="font-bold text-blue-400">Developers</span>, <span className="font-bold text-blue-400">Managers</span>, and <span className="font-bold text-blue-400">Admins</span> from the <span className="font-bold text-blue-400">Team</span> button below.
              </p>
            </div>
          ) : null}
          <div className="grid grid-cols-1 gap-4 px-4">
            <a href="/schedule">
              <div className={styles.container}>
                <BsCalendarFill size={iconSize} />
                <h3 className={styles.text}>Schedule</h3>
              </div>
            </a>
            {admin ? (
              <a href="/team">
                <div className={styles.container}>
                  <RiTeamFill size={iconSize} />
                  <h3 className={styles.text}>Team</h3>
                </div>
              </a>
            ) : (
              <a href="/clients">
                <div className={styles.container}>
                  <BsPersonFill size={iconSize} />
                  <h3 className={styles.text}>Clients</h3>
                </div>
              </a>
            )}
          </div>
        </div>
      </div>
      <Footer />
    </>
  );
};

export default Home;
