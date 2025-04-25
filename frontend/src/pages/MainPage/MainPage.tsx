
import { Navigate } from "react-router-dom";
import { getDefaultPage } from "../../utils/authorization";
import { useAuth } from "../../hooks";

export const RedirectByRole = () => {
    const { currentUser } = useAuth();
    return <Navigate to={getDefaultPage(currentUser)} />;
}

export default RedirectByRole;