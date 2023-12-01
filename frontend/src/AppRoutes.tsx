import { lazy } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import LoremIpsum from "./pages/LoremIpsum";
import PrivateRoute from "./core/components/PrivateRoute";
import RegisterConfirm from "./pages/AuthRegisterConfirm";
import Logout from "./pages/AuthLogout";

// Admin
const Admin = lazy(() => import("./admin/components/Admin"));
const AdminAppBar = lazy(() => import("./admin/components/AdminAppBar"));
const AdminToolbar = lazy(() => import("./admin/components/AdminToolbar"));

const Join = lazy(() => import("./pages/Join"));
const TeamManagement = lazy(() => import("./pages/TeamManagement"));
const Teams = lazy(() => import("./pages/Teams"));
const Issues = lazy(() => import("./pages/Issue"));
const NewIssue = lazy(() => import("./pages/IssueNew"));
const IssueEdit = lazy(() => import("./pages/IssueEdit"));



// Auth
const ForgotPassword = lazy(() => import("./pages/AuthForgotPassword"));
const ForgotPasswordConfirm = lazy(() => import("./pages/AuthForgotPasswordConfirm"));
const Login = lazy(() => import("./pages/AuthLogin"));
const Register = lazy(() => import("./pages/AuthRegister"));

// Core
const Forbidden = lazy(() => import("./pages/Forbidden"));
const NotFound = lazy(() => import("./pages/NotFound"));
const UnderConstructions = lazy(() => import("./pages/UnderConstructions"));

// Users

const AppRoutes = () => {
  return (
    <Routes basename={process.env.PUBLIC_URL}>



      <Route path="/" element={<Login />} />



      <PrivateRoute
        path="join"
        element={
          <Join />
        }
        roles={["user"]}
      />




      <PrivateRoute
        path="team/:id"
        element={
          <Admin>
            <AdminAppBar>
              <AdminToolbar title="Team Management" />
            </AdminAppBar>
            <TeamManagement />
          </Admin>
        }
        roles={["user"]}
      />



      <PrivateRoute
        path="team"
        element={
          <Admin>
            <AdminAppBar>
              <AdminToolbar title="Team Participations" />
            </AdminAppBar>
            <Teams />
          </Admin>
        }
        roles={["user"]}
      />




      <PrivateRoute
        path="issue"
        element={
          <Admin>
            <AdminAppBar>
              <AdminToolbar title="Support" />
            </AdminAppBar>
            <Issues />
          </Admin>
        }
        roles={["user", "admin"]}
      />


      <PrivateRoute
        path="issue/:id"
        element={
          <Admin>
            <AdminAppBar>
              <AdminToolbar title="Issue details" />
            </AdminAppBar>
            <IssueEdit />
          </Admin>
        }
        roles={["user", "admin"]}
      />


      <PrivateRoute
        path="issue-new"
        element={
          <Admin>
            <AdminAppBar>
              <AdminToolbar title="Add new issue" />
            </AdminAppBar>
            <NewIssue />
          </Admin>
        }
        roles={["user", "admin"]}
      />




      <Route path="forgot-password" element={<ForgotPassword />} />

      <Route path="forgot-password-confirm" element={<ForgotPasswordConfirm />} />
      <Route path="login" element={<Login />} />
      <Route path="logout" element={<Logout />} />
      <Route path="register" element={<Register />} />
      <Route path="register-confirm" element={<RegisterConfirm />} />
      <Route path="lorem-ipsum" element={<LoremIpsum />} />
      <Route path="under-construction" element={<UnderConstructions />} />
      <Route path="403" element={<Forbidden />} />
      <Route path="404" element={<NotFound />} />
      <Route
        path="*"
        element={<Navigate to={`/${process.env.PUBLIC_URL}/404`} replace />}
      />

    </Routes >
  );
};

export default AppRoutes;
