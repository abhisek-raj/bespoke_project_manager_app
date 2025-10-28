import { useEffect, useState } from "react";
import axios from "axios";
import toast, { Toaster } from "react-hot-toast";
import { config } from "../config";
import Footer from "../components/Footer";

interface Task {
  id: number;
  title: string;
  description?: string;
  status: string;
  priority: string;
  dueDate: string;
  project: {
    id: number;
    name: string;
  };
  assignedTo: {
    id: number;
    name: string;
  };
  createdDate: string;
  updatedDate: string;
}

interface Project {
  id: number;
  name: string;
  description?: string;
  status: string;
  startDate: string;
  dueDate: string;
  customer: {
    id: number;
    name: string;
  };
}

interface Developer {
  id: number;
  name: string;
  email: string;
}

const ProjectManager = (props: any) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [developers, setDevelopers] = useState<Developer[]>([]);
  const [loading, setLoading] = useState(true);

  // New task form state
  const [showNewTask, setShowNewTask] = useState(false);
  const [taskTitle, setTaskTitle] = useState("");
  const [taskDescription, setTaskDescription] = useState("");
  const [selectedProject, setSelectedProject] = useState<number>(0);
  const [selectedDeveloper, setSelectedDeveloper] = useState<number>(0);
  const [taskDueDate, setTaskDueDate] = useState("");
  const [taskPriority, setTaskPriority] = useState("medium");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      // Load projects
      const projectsResponse = await axios({
        method: "GET",
        url: `${config.apiUrl}/projects/list`,
        headers: {
          Authorization: "Bearer " + props.token,
        },
      });
      setProjects(projectsResponse.data.projects);

      // Load tasks
      const tasksResponse = await axios({
        method: "GET",
        url: "${config.apiUrl}/tasks/list",
        headers: {
          Authorization: "Bearer " + props.token,
        },
      });
      setTasks(tasksResponse.data.tasks);

      // Load developers (filter employees with Role='developer')
      const employeesResponse = await axios({
        method: "GET",
        url: "${config.apiUrl}/employees",
        headers: {
          Authorization: "Bearer " + props.token,
        },
      });
      // Normalize employee objects and filter developers. Support multiple possible backend shapes.
      const allEmployees: any[] = employeesResponse.data || [];
      console.log("Employees response:", allEmployees);
      
      // Debug logging
      console.log("All employees before filtering:", allEmployees.map(emp => ({
        id: emp.Employeeid || emp.id,
        name: `${emp.FirstName || emp.fN} ${emp.LastName || emp.lN}`,
        role: emp.Role || emp.role
      })));

      const devs = allEmployees
        .map((dev: any) => {
          const id = dev.id ?? dev.Employeeid ?? dev.EmployeeId ?? dev.employeeId;
          const first = dev.fN ?? dev.FirstName ?? dev.firstName ?? dev.first_name ?? "";
          const last = dev.lN ?? dev.LastName ?? dev.lastName ?? dev.last_name ?? "";
          const role = dev.role ?? dev.Role ?? "";
          return {
            raw: dev,
            id: typeof id === "number" ? id : Number(id) || 0,
            name: `${first} ${last}`.trim(),
            role,
          };
        })
        .filter((e) => e.role.toLowerCase() === "developer");

      const filteredDevs = devs.map((d) => ({ 
        id: d.id, 
        name: d.name, 
        email: d.raw?.email ?? d.raw?.Email 
      }));
      
      console.log("Filtered developers:", filteredDevs);
      setDevelopers(filteredDevs);
    } catch (error) {
      console.error("Error loading data:", error);
      toast.error("Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  const createTask = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios({
        method: "POST",
        url: "${config.apiUrl}/tasks/create",
        headers: {
          Authorization: "Bearer " + props.token,
        },
        data: {
          Title: taskTitle,
          Description: taskDescription,
          ProjectID: selectedProject,
          AssignedTo: selectedDeveloper,
          DueDate: taskDueDate,
          Priority: taskPriority,
        },
      });

      toast.success("Task created successfully");
      setShowNewTask(false);
      clearTaskForm();
      loadData(); // Refresh tasks list
    } catch (error) {
      console.error("Error creating task:", error);
      toast.error("Failed to create task");
    }
  };

  const updateTaskStatus = async (taskId: number, newStatus: string) => {
    try {
      await axios({
        method: "POST",
        url: "${config.apiUrl}/tasks/update",
        headers: {
          Authorization: "Bearer " + props.token,
        },
        data: {
          TaskID: taskId,
          Status: newStatus,
        },
      });

      toast.success("Task status updated");
      loadData(); // Refresh tasks list
    } catch (error) {
      console.error("Error updating task:", error);
      toast.error("Failed to update task");
    }
  };

  const clearTaskForm = () => {
    setTaskTitle("");
    setTaskDescription("");
    setSelectedProject(0);
    setSelectedDeveloper(0);
    setTaskDueDate("");
    setTaskPriority("medium");
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <>
      <Toaster />
      <div className="container mx-auto px-4 py-8">
        <div className="bg-slate-700 rounded-lg p-6 mb-8">
          <h1 className="text-3xl font-bold text-white mb-4">Project Manager Dashboard</h1>
          <div className="flex justify-between items-center">
            <p className="text-gray-300">
              Managing {projects.length} Projects and {tasks.length} Tasks
            </p>
            <button
              onClick={() => setShowNewTask(!showNewTask)}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
            >
              {showNewTask ? "Cancel" : "Create New Task"}
            </button>
          </div>

          {/* New Task Form */}
          {showNewTask && (
            <div className="mt-6 bg-slate-800 rounded-lg p-6">
              <h2 className="text-xl font-bold text-white mb-4">Create New Task</h2>
              <form onSubmit={createTask} className="space-y-4">
                <div>
                  <label className="block text-gray-300 mb-2">Title</label>
                  <input
                    type="text"
                    value={taskTitle}
                    onChange={(e) => setTaskTitle(e.target.value)}
                    className="w-full p-2 rounded bg-slate-700 text-white"
                    required
                  />
                </div>
                <div>
                  <label className="block text-gray-300 mb-2">Description</label>
                  <textarea
                    value={taskDescription}
                    onChange={(e) => setTaskDescription(e.target.value)}
                    className="w-full p-2 rounded bg-slate-700 text-white"
                    rows={3}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-gray-300 mb-2">Project</label>
                    <select
                      value={selectedProject}
                      onChange={(e) => setSelectedProject(Number(e.target.value))}
                      className="w-full p-2 rounded bg-slate-700 text-white"
                      required
                    >
                      <option value={0}>Select Project</option>
                      {projects.map((project) => (
                        <option key={project.id} value={project.id}>
                          {project.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-gray-300 mb-2">Assign To</label>
                    <select
                      value={selectedDeveloper}
                      onChange={(e) => setSelectedDeveloper(Number(e.target.value))}
                      className="w-full p-2 rounded bg-slate-700 text-white"
                    >
                      <option value={0}>Select Developer</option>
                      {developers.map((dev) => (
                        <option key={dev.id} value={dev.id}>
                          {dev.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-gray-300 mb-2">Due Date</label>
                    <input
                      type="date"
                      value={taskDueDate}
                      onChange={(e) => setTaskDueDate(e.target.value)}
                      className="w-full p-2 rounded bg-slate-700 text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-gray-300 mb-2">Priority</label>
                    <select
                      value={taskPriority}
                      onChange={(e) => setTaskPriority(e.target.value)}
                      className="w-full p-2 rounded bg-slate-700 text-white"
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                    </select>
                  </div>
                </div>
                <button
                  type="submit"
                  className="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600 transition-colors"
                >
                  Create Task
                </button>
              </form>
            </div>
          )}

          {/* Tasks List */}
          <div className="mt-8">
            <h2 className="text-xl font-bold text-white mb-4">Tasks</h2>
            <div className="grid gap-4">
              {tasks.map((task) => (
                <div
                  key={task.id}
                  className="bg-slate-800 rounded-lg p-4 flex justify-between items-start"
                >
                  <div>
                    <h3 className="text-lg font-semibold text-white">{task.title}</h3>
                    <p className="text-gray-400 mt-1">{task.description}</p>
                    <div className="mt-2 space-y-1">
                      <p className="text-gray-300 text-sm">
                        Project: {task.project.name}
                      </p>
                      <p className="text-gray-300 text-sm">
                        Assigned to: {task.assignedTo.name}
                      </p>
                      <p className="text-gray-300 text-sm">Due: {task.dueDate}</p>
                    </div>
                  </div>
                  <div className="flex flex-col items-end space-y-2">
                    <span
                      className={`px-3 py-1 rounded text-sm font-semibold ${
                        task.priority === "high"
                          ? "bg-red-500"
                          : task.priority === "medium"
                          ? "bg-yellow-500"
                          : "bg-green-500"
                      }`}
                    >
                      {task.priority}
                    </span>
                    <select
                      value={task.status}
                      onChange={(e) => updateTaskStatus(task.id, e.target.value)}
                      className="bg-slate-700 text-white rounded p-1 text-sm"
                    >
                      <option value="pending">Pending</option>
                      <option value="in_progress">In Progress</option>
                      <option value="completed">Completed</option>
                    </select>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
      <Footer />
    </>
  );
};

export default ProjectManager;
