import { useState } from "react";
import MyErrorBoundary from "../../core/components/MyErrorBoundary";
import SettingsDrawer from "../../core/components/SettingsDrawer";
import { useSettings } from "../../core/contexts/SettingsProvider";
import AdminDrawer from "./AdminDrawer";
import { PropsWithChildren } from 'react'
import Box from "@mui/material/Box/Box";
import Toolbar from "@mui/material/Toolbar/Toolbar";

type Props = {
}

export const AdminLayout = (props: PropsWithChildren<Props>) => {
  // const AdminLayout = () => {
  const [settingsOpen, setSettingsOpen] = useState(false);

  const { collapsed, open, toggleDrawer } = useSettings();

  const handleSettingsToggle = () => {
    setSettingsOpen(!settingsOpen);
  };

  return (
    <Box sx={{ display: "flex" }}>
      <AdminDrawer
        collapsed={collapsed}
        mobileOpen={open}
        onDrawerToggle={toggleDrawer}
        onSettingsToggle={handleSettingsToggle}
      />
      <SettingsDrawer
        onDrawerToggle={handleSettingsToggle}
        open={settingsOpen}
      />
      <Box component="main" sx={{ flexGrow: 1, pb: 3, px: { xs: 3, sm: 6 } }}>
        <Toolbar />
        <MyErrorBoundary>
          {/* <Outlet /> */}
          {props.children}
        </MyErrorBoundary>
      </Box>
    </Box>
  );
};

export default AdminLayout;
