import { useEffect, useState } from "react";
import axios from "axios";
import { FiEdit } from "react-icons/fi";
import { MdOutlineDeleteOutline } from "react-icons/md";

interface Project {
  id: number;
  name: string;
  description: string;
  status: string;
  startDate: string;
  dueDate: string;
  customer: {
    id: number;
    name: string;
  };
  manager: {
    id: number;
    name: string;
  };
}

const Projects = (props: any) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [role, setRole] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Fetch projects
  const fetchProjects = () => {
    axios({
      method: "GET",
      url: "http://127.0.0.1:3000/projects/list",
      headers: {
        Authorization: "Bearer " + props.token,
      },
    })
      .then((response) => {
        setProjects(response.data.projects);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching projects:", error);
        setError("Failed to load projects");
        setLoading(false);
      });
  };

  // Get user role
  const getUserRole = () => {
    axios({
      method: "GET",
      url: "http://127.0.0.1:3000/profile",
      headers: {
        Authorization: "Bearer " + props.token,
      },
    })
      .then((response) => {
        setRole(response.data.Role);
      })
      .catch((error) => {
        console.error("Error fetching user role:", error);
      });
  };

  useEffect(() => {
    getUserRole();
    fetchProjects();
  }, []);

  const handleCreateProject = () => {
    // Implement project creation logic
  };

  const handleEditProject = (projectId: number) => {
    // Implement project editing logic
  };

  const handleDeleteProject = (projectId: number) => {
    // Implement project deletion logic
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "pending":
        return "bg-yellow-200 text-yellow-800";
      case "in_progress":
        return "bg-blue-200 text-blue-800";
      case "completed":
        return "bg-green-200 text-green-800";
      default:
        return "bg-gray-200 text-gray-800";
    }
  };

  if (loading) {
    return <div className="text-center p-4">Loading...</div>;
  }

  if (error) {
    return <div className="text-center text-red-500 p-4">{error}</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Projects</h1>
        {(role === "admin" || role === "project_manager") && (
          <button
            onClick={handleCreateProject}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
          >
            Create New Project
          </button>
        )}
      </div>

      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Project Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Client
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Due Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Manager
              </th>
              {(role === "admin" || role === "project_manager") && (
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              )}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {projects.map((project) => (
              <tr key={project.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {project.name}
                  </div>
                  <div className="text-sm text-gray-500">
                    {project.description}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    {project.customer.name}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(
                      project.status
                    )}`}
                  >
                    {project.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {project.dueDate}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {project.manager.name}
                </td>
                {(role === "admin" || role === "project_manager") && (
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleEditProject(project.id)}
                      className="text-indigo-600 hover:text-indigo-900 mr-4"
                    >
                      <FiEdit size={20} />
                    </button>
                    <button
                      onClick={() => handleDeleteProject(project.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      <MdOutlineDeleteOutline size={20} />
                    </button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Projects;