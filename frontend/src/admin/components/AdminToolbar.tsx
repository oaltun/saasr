import { useSettings } from "../../core/contexts/SettingsProvider";
import Logo from "../../core/components/Logo";
import Toolbar from "@mui/material/Toolbar/Toolbar";
import IconButton from "@mui/material/IconButton/IconButton";
import Typography from "@mui/material/Typography/Typography";
import MenuIcon from '@mui/icons-material/Menu';

type AdminToolbarProps = {
  children?: React.ReactNode;
  title?: string;
};

const AdminToolbar = ({ children, title }: AdminToolbarProps) => {
  const { toggleDrawer } = useSettings();

  return (
    <Toolbar sx={{ px: { xs: 3, sm: 6 } }}>
      <IconButton
        color="inherit"
        aria-label="open drawer"
        edge="start"
        onClick={toggleDrawer}
        sx={{
          display: { lg: "none" },
          marginRight: 2,
        }}
      >
        <MenuIcon />
      </IconButton>
      <Logo sx={{ display: { lg: "none" }, p: 4 }} />

      <Typography variant="h2" component="h1" sx={{ flexGrow: 1 }}>
        {title}
      </Typography>
      {children}
    </Toolbar>
  );
};

export default AdminToolbar;
