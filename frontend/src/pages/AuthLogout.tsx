import Box from "@mui/material/Box";
import { useEffect } from "react";

import { logout } from "../auth/utils/auth";
const Logout = () => {
  useEffect(() => {
    HandleLogout();
  }, []);

  const HandleLogout = () => {
    logout();
  };

  return <Box></Box>;
};

export default Logout;
