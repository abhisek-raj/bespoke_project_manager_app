import { BrowserRouter, Routes, Route } from "react-router-dom";
import Signin from "./pages/Signin";
import Schedule from "./pages/Schedule";
import Clients from "./pages/Clients";
import Home from "./pages/Home";
import Team from "./pages/Team";
import Developer from "./pages/Developer";
import ProjectManager from "./pages/ProjectManager";
import useToken from "./components/useToken";
import Navbar from "./components/Navbar";
import History from "./pages/History";
import Projects from "./pages/Projects";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  const { token, removeToken, setToken } = useToken();

  const renderLayout = (Component: React.ComponentType<any>, allowedRoles?: string[]) => (
    <>
      <Navbar token={token} setToken={setToken} removeToken={removeToken} />
      {allowedRoles && allowedRoles.length > 0 ? (
        <ProtectedRoute token={token} allowedRoles={allowedRoles}>
          <Component token={token} setToken={setToken} removeToken={removeToken} />
        </ProtectedRoute>
      ) : (
        <Component token={token} setToken={setToken} removeToken={removeToken} />
      )}
    </>
  );

  return (
    <BrowserRouter>
      {!token && token !== "" && token !== undefined ? (
        <Signin setToken={setToken} />
      ) : (
        <>
          <Routes>
            <Route path="/*" element={renderLayout(Home)} />
            <Route path="/schedule" element={renderLayout(Schedule)} />
            <Route path="/clients" element={renderLayout(Clients, ["admin", "project_manager"])} />
            <Route path="/history/:customerID" element={renderLayout(History)} />
            <Route path="/team" element={renderLayout(Team, ["admin"])} />
            <Route path="/developer" element={renderLayout(Developer, ["developer"])} />
            <Route path="/projectmanager" element={renderLayout(ProjectManager, ["project_manager"])} />
            <Route path="/projects" element={renderLayout(Projects)} />
          </Routes>
        </>
      )}
    </BrowserRouter>
  );
}

export default App;
