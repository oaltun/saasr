import { Navigate, Route, RouteProps } from "react-router";
import { useAuth } from "../../auth/contexts/AuthProvider";
import Forbidden from "../../pages/Forbidden";


type PrivateRouteProps = {
  roles?: string[];
} & RouteProps;

const PrivateRoute = ({
  children,
  roles = [],
  ...routeProps
}: PrivateRouteProps) => {
  const auth = useAuth();

  if (auth.expired())
    return <Navigate to={`/${process.env.PUBLIC_URL}/login`} />;

  if (!auth.hasRole(roles)) {
    const message = "You do not have any valid roles in this route."
      + (auth.userInfo ? " Your roles: " + auth.userInfo?.roles.toString() + "." : "")
      + (roles ? " Needed roles: " + roles?.toString() + "." : "");
    return < Forbidden message={message} />
  }

  return <Route {...routeProps} />;

};

export default PrivateRoute;
