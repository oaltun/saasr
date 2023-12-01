import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Result from '../core/components/Result';
import { ReactComponent as WelcomeSVG } from "../core/assets/welcome.svg";
import Card from '@mui/material/Card';

import Button from '@mui/material/Button/Button';
// ======= //
// RENDER
// ======= //
// MUI page sizes: xs, sm, md, lg, and xl
// when you set a value for one, it is valid for larger page sizes too.
// unless that value for larger is specified too.
const LoremIpsum = () => {
    const onButtonClick = () => {
        console.log("process.env");
        console.log(process.env);
    }

    return (
        <Box sx={{ width: '100%', maxWidth: 500 }}>

            <Button onClick={onButtonClick}>My Btton</Button>
            <Typography variant="h1" gutterBottom>
                h1. Heading
            </Typography>
            <Typography variant="h2" gutterBottom>
                h2. Heading
            </Typography>
            <Typography variant="h3" gutterBottom>
                h3. Heading
            </Typography>
            <Typography variant="h4" gutterBottom>
                h4. Heading
            </Typography>
            <Typography variant="h5" gutterBottom>
                h5. Heading
            </Typography>
            <Typography variant="h6" gutterBottom>
                h6. Heading
            </Typography>
            <Typography variant="subtitle1" gutterBottom>
                subtitle1. Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quos
                blanditiis tenetur
            </Typography>
            <Typography variant="subtitle2" gutterBottom>
                subtitle2. Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quos
                blanditiis tenetur
            </Typography>
            <Typography variant="body1" gutterBottom>
                body1. Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quos
                blanditiis tenetur unde suscipit, quam beatae rerum inventore consectetur,
                neque doloribus, cupiditate numquam dignissimos laborum fugiat deleniti? Eum
                quasi quidem quibusdam.
            </Typography>
            <Typography variant="body2" gutterBottom>
                body2. Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quos
                blanditiis tenetur unde suscipit, quam beatae rerum inventore consectetur,
                neque doloribus, cupiditate numquam dignissimos laborum fugiat deleniti? Eum
                quasi quidem quibusdam.
            </Typography>
            <Typography variant="button" display="block" gutterBottom>
                button text
            </Typography>
            <Typography variant="caption" display="block" gutterBottom>
                caption text
            </Typography>
            <Typography variant="overline" display="block" gutterBottom>
                overline text
            </Typography>
            <hr />
            <Card>
                <Result extra="I am the extra" image={<WelcomeSVG />} title="I am used for result pages" maxWidth='sm' status='success' subTitle='I am the subtitle. Lorem I am the subtitle. Lorem I am the subtitle.' />
            </Card>
        </Box>
    );
};




export default LoremIpsum;
