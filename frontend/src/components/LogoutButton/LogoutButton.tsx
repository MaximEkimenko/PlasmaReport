import { Button } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { clearStore } from "../../utils/local-storage";
import { useAuth } from "../../hooks";
import { endpoints } from "../../utils/authorization.ts";

const LogoutButton = () => {
    const navigate = useNavigate();
    const uc = useAuth();
    if (uc) {
        const { logout } = uc;
        const handleLogout = async () => {
            clearStore();
            logout()
            navigate(endpoints.LOGIN);
        };

        return (
            <>
                <Button size="small" variant="contained" onClick={handleLogout}>
                    выйти
                </Button>
            </>
        );
    } else {
        return (
            <>
                <Button size="small" variant="contained">
                    не работает
                </Button>
            </>
        );
    }
};
export default LogoutButton;
