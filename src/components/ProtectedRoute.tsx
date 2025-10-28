import { useState, useEffect } from "react";
import { Navigate } from "react-router-dom";
import axios from "axios";
import { config } from "../config";

interface ProtectedRouteProps {
  token?: string | null;
  allowedRoles: string[];
  children: React.ReactNode;
}

const ProtectedRoute = ({ token, allowedRoles, children }: ProtectedRouteProps) => {
  const [role, setRole] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const getUserRole = async () => {
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const response = await axios({
          method: "GET",
          url: `${config.apiUrl}/profile`,
          headers: {
            Authorization: "Bearer " + token,
          },
        });
        // Respect legacy Admin flag as well as Role field.
        // If backend returns Admin=true, treat user as 'admin' regardless of Role value.
        const resp = response.data;
        if (resp && resp.Admin) {
          setRole("admin");
        } else {
          setRole(resp ? resp.Role : null);
        }
      } catch (error) {
        console.error("Error fetching user role:", error);
      } finally {
        setLoading(false);
      }
    };

    getUserRole();
  }, [token]);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!role || !allowedRoles.includes(role)) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;